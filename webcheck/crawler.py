
# crawler.py - definition of Link class for storing the crawled site
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
# Copyright (C) 2005, 2006, 2007, 2008, 2011, 2013 Arthur de Jong
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
import logging
import os
import re
import robotparser
import time
import urllib2
import urlparse

from webcheck import config
from webcheck.db import Session, Base, Link, truncate_db
from webcheck.output import install_file
import webcheck.parsers

from sqlalchemy import create_engine


logger = logging.getLogger(__name__)


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


# get default configuration
default_cfg = dict(
    internal=[], external=[], yank=[], base_only=config.BASE_URLS_ONLY,
    avoid_external=config.AVOID_EXTERNAL_LINKS, ignore_robots=not(config.USE_ROBOTS),
    output=config.OUTPUT_DIR, force=config.OVERWRITE_FILES,
    redirects=config.REDIRECT_DEPTH, max_depth=config.MAX_DEPTH,
    wait=config.WAIT_BETWEEN_REQUESTS)
default_cfg.update({'continue': config.CONTINUE})


class Config(object):

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def update(self, *args, **kwargs):
        for arg in args:
            vars(self).update(arg)
        vars(self).update(kwargs)


class Crawler(object):
    """Class to represent gathered data of a site.

    The available properties of this class are:

      site_name  - the name of the website that is crawled
      bases      - a list of base link object
      plugins    - a list of plugin modules used by the crawler
    """

    def __init__(self, cfg):
        """Creates an instance of the Crawler class and initializes the
        state of the site."""
        # complete the configuration
        self.cfg = Config(default_cfg)
        self.cfg.update(cfg)
        # list of regexps considered internal
        self._internal_res = {}
        for pattern in self.cfg.internal:
            self._internal_res[pattern] = re.compile(pattern, re.IGNORECASE)
        # list of regexps considered external
        self._external_res = {}
        for pattern in self.cfg.external:
            self._external_res[pattern] = re.compile(pattern, re.IGNORECASE)
        # list of regexps matching links that should not be checked
        self._yanked_res = {}
        for pattern in self.cfg.yank:
            self._yanked_res[pattern] = re.compile(pattern, re.IGNORECASE)
        # update other configuration
        config.BASE_URLS_ONLY = self.cfg.base_only
        config.AVOID_EXTERNAL_LINKS = self.cfg.avoid_external
        config.USE_ROBOTS = not(self.cfg.ignore_robots)
        config.OUTPUT_DIR = self.cfg.output_dir
        config.CONTINUE = getattr(self.cfg, 'continue')
        config.OVERWRITE_FILES = self.cfg.force
        config.REDIRECT_DEPTH = self.cfg.redirects
        config.MAX_DEPTH = self.cfg.max_depth
        config.WAIT_BETWEEN_REQUESTS = self.cfg.wait
        # map of scheme+netloc to robot parsers
        self._robotparsers = {}
        # set up empty site name
        self.site_name = None
        # load the plugins
        self.plugins = [
            __import__(plugin, globals(), locals(), [plugin])
            for plugin in config.PLUGINS]
        # add base urls
        self._internal_urls = set()
        for url in self.cfg.base_urls:
            # if it does not look like a url it is probably a local file
            if urlparse.urlsplit(url)[0] == '':
                url = 'file://' + urllib.pathname2url(os.path.abspath(url))
            # clean the URL and add it
            url = Link.clean_url(url)
            if url not in self._internal_urls:
                self._internal_urls.add(url)
        # list of base link objects
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
            logger.debug('called with unsupported scheme (%s)', scheme)
            return None
        # split out the key part of the url
        location = urlparse.urlunsplit((scheme, netloc, '', '', ''))
        # try to create a new robotparser if we don't already have one
        if location not in self._robotparsers:
            logger.info('getting robots.txt for %s', location)
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
        if config.MAX_DEPTH != None:
            links = links.filter(Link.depth <= config.MAX_DEPTH)
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
            link.yanked = self._is_yanked(str(link.url))
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
                logger.debug('sleeping %s seconds',
                             config.WAIT_BETWEEN_REQUESTS)
                time.sleep(config.WAIT_BETWEEN_REQUESTS)
            logger.debug('items left to check: %d' %
                          (remaining + len(tocheck)))
        session.commit()
        session.close()

    def fetch(self, link):
        """Attempt to fetch the url (if not yanked) and fill in link
        attributes (based on is_internal)."""
        logger.info(link.url)
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
            info = response.info()
            link.mimetype = response.info().gettype()
            link.set_encoding(response.headers.getparam('charset'))
            # get result code and other stuff
            link.status = str(response.code)
            try:
                link.size = int(info.getheader('Content-length'))
            except (TypeError, ValueError):
                pass
            mtime = info.getdate('Last-Modified')
            if mtime:
                link.mtime = datetime.datetime(*mtime[:7])
            # if response.status == 301: link.add_linkproblem(str(response.status)+': '+response.reason)
            # elif response.status != 200: link.add_linkproblem(str(response.status)+': '+response.reason)
            # TODO: add checking for size
            return response
        except RedirectError, e:
            link.status = str(e.code)
            logger.info(str(e))
            if e.code == 301:
                link.add_linkproblem(str(e))
            link.add_redirect(e.newurl)
        except urllib2.HTTPError, e:
            link.status = str(e.code)
            logger.info(str(e))
            link.add_linkproblem(str(e))
        except urllib2.URLError, e:
            logger.info(str(e))
            link.add_linkproblem(str(e))
        except KeyboardInterrupt:
            # handle this in a higher-level exception handler
            raise
        except Exception, e:
            # handle all other exceptions
            logger.exception('unknown exception caught: ' + str(e))
            link.add_linkproblem('error reading HTTP response: %s' % str(e))

    def parse(self, link, response):
        """Parse the fetched response."""
        # find a parser for the content-type
        parsermodule = webcheck.parsers.get_parsermodule(link.mimetype)
        if parsermodule is None:
            logger.debug('unsupported content-type: %s', link.mimetype)
            return
        try:
            # skip parsing of content if we were returned nothing
            content = response.read()
            if content is None:
                return
            # parse the content
            logger.debug('parsing using %s', parsermodule.__name__)
            parsermodule.parse(content, link)
        except KeyboardInterrupt:
            # handle this in a higher-level exception handler
            raise
        except Exception, e:
            logger.exception('problem parsing page: %s', str(e))
            link.add_pageproblem('problem parsing page: %s' % str(e))

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
                logger.warn('base link %s redirects to nowhere', url)
                continue
            # add the link to bases
            logger.debug('adding %s to bases', link.url)
            self.bases.append(link)
        # if we got no bases, just use the first internal one
        if not self.bases:
            link = session.query(Link).filter(Link.is_internal == True).first()
            logger.debug('fallback to adding %s to bases', link.url)
            self.bases.append(link)
        # set the site name
        self.site_name = self.bases[0].title or self.bases[0].url
        # do a breadth first traversal of the website to determine depth
        session.query(Link).update(dict(depth=None), synchronize_session=False)
        session.commit()
        depth = 0
        count = len(self.bases)
        for link in self.bases:
            link.depth = 0
        session.commit()
        while count > 0:
            logger.debug('%d links at depth %d%s', count, depth,
                         ' (max)' if depth == config.MAX_DEPTH else '')
            # update the depth of all links without a depth that have a
            # parent with the previous depth
            qry = session.query(Link).filter(Link.depth == None)
            qry = qry.filter(Link.linked_from.any(Link.depth == depth))
            count = qry.update(dict(depth=depth + 1), synchronize_session=False)
            session.commit()
            depth += 1
            # TODO: also handle embeds
        # see if any of the plugins want to do postprocessing
        for plugin in self.plugins:
            if hasattr(plugin, 'postprocess'):
                logger.info(plugin.__name__)
                plugin.postprocess(self)
        #session.close() do not close because bases uses the session

    def generate(self):
        """Generate pages for plugins."""
        # ensure we have a connection to the database
        self.setup_database()
        # call all the plugins
        for plugin in self.plugins:
            if hasattr(plugin, 'generate'):
                logger.info(plugin.__name__)
                plugin.generate(self)
        # install theme files
        install_file('webcheck.css', True)
        install_file('fancytooltips/fancytooltips.js', True)
        install_file('favicon.ico', False)
