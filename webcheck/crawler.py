
# crawler.py - definition of Link class for storing the crawled site
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
# Copyright (C) 2005, 2006, 2007, 2008, 2011 Arthur de Jong
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# The files produced as output from the software do not automatically fall
# under the copyright of the software, unless explicitly stated otherwise.

"""General module to do site-checking. This module contains the Crawler class
containing the state for the crawled site and some functions to access and
manipulate the crawling of the website. This module also contains the Link
class that holds all the link related properties."""

import atexit
import cookielib
import datetime
import httplib
import os
import re
import robotparser
import time
import urllib2
import urlparse

from webcheck import config, debugio
from webcheck.db import Session, Base, Link
from webcheck.util import install_file
import webcheck.parsers

from sqlalchemy import create_engine


class RedirectError(urllib2.HTTPError):

    def __init__(self, url, code, msg, hdrs, fp, newurl):
        self.newurl = newurl
        urllib2.HTTPError.__init__(self, url, code, msg, hdrs, fp)


class NoRedirectHandler(urllib2.HTTPRedirectHandler):

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RedirectError(req.get_full_url(), code, msg, headers, fp, newurl)


def _setup_urllib2():
    """Configure the urllib2 module to store cookies in the output
    directory."""
    import webcheck  # local import to avoid import loop
    filename = os.path.join(config.OUTPUT_DIR, 'cookies.txt')
    # set up our cookie jar
    cookiejar = cookielib.MozillaCookieJar(filename)
    try:
        cookiejar.load(ignore_discard=False, ignore_expires=False)
    except IOError:
        pass
    atexit.register(cookiejar.save, ignore_discard=False, ignore_expires=False)
    # set up our custom opener that sets a meaningful user agent
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar),
                                  NoRedirectHandler())
    opener.addheaders = [
      ('User-agent', 'webcheck %s' % webcheck.__version__),
      ]
    if config.BYPASSHTTPCACHE:
        opener.addheaders.append(('Cache-control', 'no-cache'))
        opener.addheaders.append(('Pragma', 'no-cache'))
    urllib2.install_opener(opener)


# pattern for matching spaces
_spacepattern = re.compile(' ')

# pattern to match anchor part of a url
_anchorpattern = re.compile('#([^#]+)$')


class Crawler(object):
    """Class to represent gathered data of a site.

    The available properties of this class are:

      bases      - a list of base link object
   """

    def __init__(self):
        """Creates an instance of the Crawler class and initializes the
        state of the site."""
        # list of internal urls
        self._internal_urls = set()
        # list of regexps considered internal
        self._internal_res = {}
        # list of regexps considered external
        self._external_res = {}
        # list of regexps matching links that should not be checked
        self._yanked_res = {}
        # map of scheme+netloc to robot handleds
        self._robotparsers = {}
        # list of base urls (these are the internal urls to start from)
        self.bases = []

    def setup_database(self):
        if hasattr(self, 'database_configed'):
            return
        self.database_configed = True
        # ensure output directory exists
        if not os.path.isdir(config.OUTPUT_DIR):
            os.mkdir(config.OUTPUT_DIR)
        # open the sqlite file
        filename = os.path.join(config.OUTPUT_DIR, 'webcheck.sqlite')
        engine = create_engine('sqlite:///' + filename)
        Session.configure(bind=engine)
        # ensure that all tables are created
        Base.metadata.create_all(engine)
        # TODO: schema migraton goes here

    def add_base(self, url):
        """Add the given url and consider all urls below it to be internal.
        These links are all marked for checking with the crawl() function."""
        # ensure we have a connection to the database
        self.setup_database()
        # clean the URL and add it
        url = Link.clean_url(url)
        if url not in self._internal_urls:
            self._internal_urls.add(url)

    def add_internal_re(self, exp):
        """Adds the gived regular expression as a pattern to match internal
        urls."""
        self._internal_res[exp] = re.compile(exp, re.IGNORECASE)

    def add_external_re(self, exp):
        """Adds the gived regular expression as a pattern to match external
        urls."""
        self._external_res[exp] = re.compile(exp, re.IGNORECASE)

    def add_yanked_re(self, exp):
        """Adds the gived regular expression as a pattern to match urls that
        will not be checked at all."""
        self._yanked_res[exp] = re.compile(exp, re.IGNORECASE)

    def _is_internal(self, url):
        """Check whether the specified url is external or internal. This
        uses the urls marked with add_base() and the regular expressions
        passed with add_external_re()."""
        # check if it is internal through the regexps
        for regexp in self._internal_res.values():
            if regexp.search(url) is not None:
                return True
        res = False
        # check that the url starts with an internal url
        if config.BASE_URLS_ONLY:
            # the url must start with one of the _internal_urls
            for i in self._internal_urls:
                res |= (i == url[:len(i)])
        else:
            # the netloc must match a netloc of an _internal_url
            netloc = urlparse.urlsplit(url)[1]
            for i in self._internal_urls:
                res |= (urlparse.urlsplit(i)[1] == netloc)
        # if it is not internal now, it never will be
        if not res:
            return False
        # check if it is external through the regexps
        for x in self._external_res.values():
            # if the url matches it is external and we can stop
            if x.search(url):
                return False
        return True

    def _get_robotparser(self, scheme, netloc):
        """Return the proper robots parser for the given url or None if one
        cannot be constructed. Robot parsers are cached per scheme and
        netloc."""
        # only some schemes have a meaningful robots.txt file
        if scheme != 'http' and scheme != 'https':
            debugio.debug('crawler._get_robotparser() '
                          'called with unsupported scheme (%s)' % scheme)
            return None
        # split out the key part of the url
        location = urlparse.urlunsplit((scheme, netloc, '', '', ''))
        # try to create a new robotparser if we don't already have one
        if location not in self._robotparsers:
            debugio.info('  getting robots.txt for %s' % location)
            self._robotparsers[location] = None
            try:
                rp = robotparser.RobotFileParser()
                rp.set_url(urlparse.urlunsplit(
                  (scheme, netloc, '/robots.txt', '', '')))
                rp.read()
                self._robotparsers[location] = rp
            except (TypeError, IOError, httplib.HTTPException):
                # ignore any problems setting up robot parser
                pass
        return self._robotparsers[location]

    def _is_yanked(self, url):
        """Check whether the specified url should not be checked at all.
        This uses the regualr expressions passed with add_yanked_re() and the
        robots information present."""
        # check if it is yanked through the regexps
        for regexp in self._yanked_res.values():
            # if the url matches it is yanked and we can stop
            if regexp.search(url):
                return 'yanked'
        # check if we should avoid external links
        is_internal = self._is_internal(url)
        if not is_internal and config.AVOID_EXTERNAL_LINKS:
            return 'external avoided'
        # check if we should use robot parsers
        if not config.USE_ROBOTS:
            return None
        (scheme, netloc) = urlparse.urlsplit(url)[0:2]
        # skip schemes not having robot.txt files
        if scheme not in ('http', 'https'):
            return None
        # skip robot checks for external urls
        # TODO: make this configurable
        if not is_internal:
            return None
        # check robots for remaining links
        rp = self._get_robotparser(scheme, netloc)
        if rp and not rp.can_fetch('webcheck', url):
            return 'robot restriced'
        # fall back to allowing the url
        return None

    def get_link(self, session, url):
        # try to find the URL
        url = Link.clean_url(url)
        link = session.query(Link).filter_by(url=url).first()
        if not link:
            link = Link(url=url)
            session.add(link)
        return link

    def get_links_to_crawl(self, session):
        links = session.query(Link).filter(Link.fetched == None)
        return links.filter(Link.yanked == None)

    def crawl(self):
        """Crawl the website based on the urls specified with add_base().
        If the serialization file pointer is specified the crawler writes
        out updated links to the file while crawling the site."""
        # connect to the database
        self.setup_database()
        # configure urllib2 to store cookies in the output directory
        _setup_urllib2()
        # get a database session
        session = Session()
        # remove all links
        if not config.CONTINUE:
            truncate_db()
        # add all internal urls to the database
        for url in self._internal_urls:
            url = Link.clean_url(url)
            self.get_link(session, url)
        # add some URLs from the database that haven't been fetched
        tocheck = self.get_links_to_crawl(session)
        remaining = tocheck.count()
        tocheck = tocheck[:100]
        remaining -= len(tocheck)
        # repeat until we have nothing more to check
        while tocheck:
            # choose a link from the tocheck list
            link = tocheck.pop()
            link.is_internal = self._is_internal(link.url)
            link.yanked = self._is_yanked(link.url)
            # see if there are any more links to check
            if not tocheck:
                tocheck = self.get_links_to_crawl(session)
                remaining = tocheck.count()
                tocheck = tocheck[:100]
                remaining -= len(tocheck)
            # skip link it there is nothing to check
            if link.yanked or link.fetched:
                continue
            # fetch the link's contents
            response = self.fetch(link)
            if response:
                self.parse(link, response)
            # flush database changes
            session.commit()
            # sleep between requests if configured
            if config.WAIT_BETWEEN_REQUESTS > 0:
                debugio.debug('crawler.crawl(): sleeping %s seconds' %
                              config.WAIT_BETWEEN_REQUESTS)
                time.sleep(config.WAIT_BETWEEN_REQUESTS)
            debugio.debug('crawler.crawl(): items left to check: %d' %
                          (remaining + len(tocheck)))
        session.commit()

    def fetch(self, link):
        """Attempt to fetch the url (if not yanked) and fill in link
        attributes (based on is_internal)."""
        debugio.info('  %s' % link.url)
        # mark the link as fetched to avoid loops
        link.fetched = datetime.datetime.now()
        # see if we can import the proper module for this scheme
        try:
            # FIXME: if an URI has a username:passwd add the uri, username and password to the HTTPPasswordMgr
            request = urllib2.Request(link.url)
            parent = link.parents.first()
            if parent:
                request.add_header('Referer', parent.url)
            response = urllib2.urlopen(request, timeout=config.IOTIMEOUT)
            link.mimetype = response.info().gettype()
            link.set_encoding(response.headers.getparam('charset'))
            # FIXME: get result code and other stuff
            link.status = str(response.code)
            # link.size = int(response.getheader('Content-length'))
            # link.mtime = time.mktime(response.msg.getdate('Last-Modified'))
            # if response.status == 301: link.add_linkproblem(str(response.status)+': '+response.reason)
            # elif response.status != 200: link.add_linkproblem(str(response.status)+': '+response.reason)
            # TODO: add checking for size
            return response
        except RedirectError, e:
            link.status = str(e.code)
            debugio.info('    ' + str(e))
            if e.code == 301:
                link.add_linkproblem(str(e))
            link.add_redirect(e.newurl)
            return
        except urllib2.HTTPError, e:
            link.status = str(e.code)
            debugio.info('    ' + str(e))
            link.add_linkproblem(str(e))
            return
        except urllib2.URLError, e:
            debugio.info('    ' + str(e))
            link.add_linkproblem(str(e))
            return
        except KeyboardInterrupt:
            # handle this in a higher-level exception handler
            raise
        except Exception, e:
            # handle all other exceptions
            debugio.warn('unknown exception caught: ' + str(e))
            link.add_linkproblem('error reading HTTP response: %s' % str(e))
            import traceback
            traceback.print_exc()
            return

    def parse(self, link, response):
        """Parse the fetched response."""
        # find a parser for the content-type
        parsermodule = webcheck.parsers.get_parsermodule(link.mimetype)
        if parsermodule is None:
            debugio.debug('crawler.Link.fetch(): unsupported content-type: %s' % link.mimetype)
            return
        try:
            # skip parsing of content if we were returned nothing
            content = response.read()
            if content is None:
                return
            # parse the content
            debugio.debug('crawler.Link.fetch(): parsing using %s' % parsermodule.__name__)
            parsermodule.parse(content, link)
        except KeyboardInterrupt:
            # handle this in a higher-level exception handler
            raise
        except Exception, e:
            import traceback
            traceback.print_exc()
            debugio.warn('problem parsing page: ' + str(e))
            link.add_pageproblem('problem parsing page: ' + str(e))

    def postprocess(self):
        """Do some basic post processing of the collected data, including
        depth calculation of every link."""
        # ensure we have a connection to the database
        self.setup_database()
        # get a database session
        session = Session()
        # build the list of urls that were set up with add_base() that
        # do not have a parent (they form the base for the site)
        for url in self._internal_urls:
            link = self.get_link(session, url).follow_link()
            if not link:
                debugio.warn('base link %s redirects to nowhere' % url)
                continue
            # add the link to bases
            debugio.debug('crawler.postprocess(): adding %s to bases' % link.url)
            self.bases.append(link)
        # if we got no bases, just use the first internal one
        if not self.bases:
            link = session.query(Link).filter(Link.is_internal == True).first()
            debugio.debug('crawler.postprocess(): fallback to adding %s to bases' % link.url)
            self.bases.append(link)
        # do a breadth first traversal of the website to determine depth
        session.query(Link).update(dict(depth=None), synchronize_session=False)
        session.commit()
        depth = 0
        count = len(self.bases)
        for link in self.bases:
            link.depth = 0
        session.commit()
        debugio.debug('crawler.postprocess(): %d links at depth 0' % count)
        while count > 0:
            # update the depth of all links without a depth that have a
            # parent with the previous depth
            qry = session.query(Link).filter(Link.depth == None)
            qry = qry.filter(Link.linked_from.any(Link.depth == depth))
            count = qry.update(dict(depth=depth + 1), synchronize_session=False)
            session.commit()
            depth += 1
            debugio.debug('crawler.postprocess(): %d links at depth %d' % (count, depth))
            # TODO: also handle embeds
        # see if any of the plugins want to do postprocessing
        for plugin in config.PLUGINS:
            # import the plugin
            pluginmod = __import__(plugin, globals(), locals(), [plugin])
            if hasattr(pluginmod, 'postprocess'):
                debugio.info('  ' + plugin)
                pluginmod.postprocess(self)

    def generate(self):
        """Generate pages for plugins."""
        # ensure we have a connection to the database
        self.setup_database()
        # call all the plugins
        for plugin in config.PLUGINS:
            # import the plugin
            pluginmod = __import__(plugin, globals(), locals(), [plugin])
            if hasattr(pluginmod, 'generate'):
                debugio.info('  ' + plugin)
                pluginmod.generate(self)
        # install theme files
        install_file('webcheck.css', True)
        install_file('fancytooltips/fancytooltips.js', True)
        install_file('favicon.ico', False)
