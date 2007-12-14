
# crawler.py - definition of Link class for storing the crawled site
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
# Copyright (C) 2005, 2006, 2007 Arthur de Jong
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

"""General module to do site-checking. This module contains the Site class
containing the state for the crawled site and some functions to access and
manipulate the crawling of the website. This module also contains the Link
class that holds all the link related properties."""

import config
import debugio
import urlparse
import urllib
import robotparser
import schemes
import parsers
import re
import time
import myurllib

# this is a workaround for Python 2.3
try:
    set
except NameError:
    from sets import Set as set

# pattern for matching spaces
_spacepattern = re.compile(' ')

# pattern to match anchor part of a url
_anchorpattern = re.compile('#([^#]+)$')

class Site:
    """Class to represent gathered data of a site.

    The available properties of this class are:

      linkMap    - a map of urls to link objects
      bases      - a list of base link object
   """

    def __init__(self):
        """Creates an instance of the Site class and initializes the
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
        # a map of urls to Link objects
        self.linkMap = {}
        # list of base urls (these are the internal urls to start from)
        self.bases = []

    def add_internal(self, url):
        """Add the given url and consider all urls below it to be internal.
        These links are all marked for checking with the crawl() function."""
        url = myurllib.normalizeurl(url)
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

    def _is_internal(self, link):
        """Check whether the specified url is external or internal.
        This uses the urls marked with add_internal() and the regular
        expressions passed with add_external_re()."""
        # check if it is internal through the regexps
        for regexp in self._internal_res.values():
            if regexp.search(link.url) is not None:
                return True
        res = False
        # check that the url starts with an internal url
        if config.BASE_URLS_ONLY:
            # the url must start with one of the _internal_urls
            for i in self._internal_urls:
                res |= (i==link.url[:len(i)])
        else:
            # the netloc must match a netloc of an _internal_url
            for i in self._internal_urls:
                res |= (urlparse.urlsplit(i)[1]==link.netloc)
        # if it is not internal now, it never will be
        if not res:
            return False
        # check if it is external through the regexps
        for x in self._external_res.values():
            # if the url matches it is external and we can stop
            if x.search(link.url) is not None:
                return False
        return True

    def _get_robotparser(self, link):
        """Return the proper robots parser for the given url or None if one
        cannot be constructed. Robot parsers are cached per scheme and
        netloc."""
        # only some schemes have a meaningful robots.txt file
        if link.scheme != 'http' and link.scheme != 'https':
            debugio.debug('crawler._get_robotparser() called with unsupported scheme (%s)' % link.scheme)
            return None
        # split out the key part of the url
        location = urlparse.urlunsplit((link.scheme, link.netloc, '', '', ''))
        # try to create a new robotparser if we don't already have one
        if not self._robotparsers.has_key(location):
            import httplib
            debugio.info('  getting robots.txt for %s' % location)
            self._robotparsers[location] = None
            try:
                rp = robotparser.RobotFileParser()
                rp.set_url(urlparse.urlunsplit(
                  (link.scheme, link.netloc, '/robots.txt', '', '') ))
                rp.read()
                self._robotparsers[location] = rp
            except (TypeError, IOError, httplib.HTTPException):
                # ignore any problems setting up robot parser
                pass
        return self._robotparsers[location]

    def _is_yanked(self, link):
        """Check whether the specified url should not be checked at all.
        This uses the regualr expressions passed with add_yanked_re() and the
        robots information present."""
        # check if it is yanked through the regexps
        for regexp in self._yanked_res.values():
            # if the url matches it is yanked and we can stop
            if regexp.search(link.url) is not None:
                return 'yanked'
        # check if we should avoid external links
        if not link.isinternal and config.AVOID_EXTERNAL_LINKS:
            return 'external avoided'
        # check if we should use robot parsers
        if not config.USE_ROBOTS:
            return False
        # skip schemes not haveing robot.txt files
        if link.scheme != 'http' and link.scheme != 'https':
            return False
        # skip robot checks for external urls
        # TODO: make this configurable
        if not link.isinternal:
            return False
        # check robots for remaining links
        rp = self._get_robotparser(link)
        if rp is not None and not rp.can_fetch('webcheck', link.url):
            return 'robot restriced'
        # fall back to allowing the url
        return False

    def get_link(self, url):
        """Return a link object for the given url.
        This function checks the map of cached link objects for an
        instance."""
        # clean the url
        url = myurllib.normalizeurl(url)
        # check if we have an object ready
        if self.linkMap.has_key(url):
            return self.linkMap[url]
        # create a new instance
        return Link(self, url)

    def crawl(self, serfp=None):
        """Crawl the website based on the urls specified with
        add_internal(). If the serialization file pointer
        is specified the crawler writes out updated links to
        the file while crawling the site."""
        # TODO: have some different scheme to crawl a site (e.g. separate
        #       internal and external queues, threading, etc)
        tocheck = set()
        # add all unfetched site urls
        for link in self.linkMap.values():
            if not link.isyanked and not link.isfetched:
                tocheck.add(link)
        # add all internal urls
        for url in self._internal_urls:
            tocheck.add(self.get_link(url))
        # repeat until we have nothing more to check
        fetchedlinks = 0
        while len(tocheck) > 0:
            debugio.debug('crawler.crawl(): items left to check: %d' % len(tocheck))
            # choose a link from the tocheck list
            link = tocheck.pop()
            # skip link it there is nothing to check
            if link.isyanked or link.isfetched:
                continue
            # fetch the link's contents
            link.fetch()
            # add children to tocheck
            for child in link.children:
                if not child.isyanked and not child.isfetched:
                    tocheck.add(child)
            # add embedded content
            for embed in link.embedded:
                if not embed.isyanked and not embed.isfetched:
                    tocheck.add(embed)
            # serialize all as of yet unserialized links
            fetchedlinks += 1
            # TODO: make this configurable
            if serfp and fetchedlinks >= 5:
                fetchedlinks = 0
                import serialize
                for link in self.linkMap.values():
                    if link._ischanged:
                        serialize.serialize_link(serfp, link)
                        link._ischanged = False
                serfp.flush()
            # sleep between requests if configured
            if config.WAIT_BETWEEN_REQUESTS > 0:
                debugio.debug('crawler.crawl(): sleeping %s seconds' % config.WAIT_BETWEEN_REQUESTS)
                time.sleep(config.WAIT_BETWEEN_REQUESTS)
        # serialize remaining changed links
        if serfp:
            import serialize
            for link in self.linkMap.values():
                if link._ischanged:
                    serialize.serialize_link(serfp, link)
                    link._ischanged = False
            serfp.flush()

    def postprocess(self):
        # build the list of urls that were set up with add_internal() that
        # do not have a parent (they form the base for the site)
        for url in self._internal_urls:
            link = self.linkMap[url].follow_link()
            if link == None:
                debugio.warn('base link %s redirects to nowhere' % url)
                continue
            # add the link to bases
            debugio.debug('crawler.postprocess(): adding %s to bases' % link.url)
            self.bases.append(link)
        # if we got no bases, just use the first internal one
        if len(self.bases) == 0:
            debugio.debug('crawler.postprocess(): fallback to adding %s to bases' % self._internal_urls[0])
            self.bases.append(self.linkMap[self._internal_urls[0]])
        # do a breadth first traversal of the website to determin depth and
        # figure out page children
        tocheck = set()
        for link in self.bases:
            link.depth = 0
            tocheck.add(link)
        # repeat until we have nothing more to check
        while len(tocheck) > 0:
            debugio.debug('crawler.postprocess(): items left to examine: %d' % len(tocheck))
            # choose a link from the tocheck list
            link = tocheck.pop()
            # figure out page children
            for child in link._pagechildren():
                # skip children with the wrong depth
                if child.depth != link.depth+1:
                    continue
                tocheck.add(child)

class Link:
    """This is a basic class representing a url.

    Some basic information about a url is stored in instances of this
    class:

      url        - the url this link represents
      scheme     - the scheme part of the url
      netloc     - the netloc part of the url
      path       - the path part of the url
      query      - the query part of the url
      parents    - list of parent links (all the Links that link to this
                   page)
      children   - list of child links (the Links that this page links to)
      pagechildren - list of child pages, including children of embedded
                     elements
      embedded   - list of links to embeded content
      anchors    - list of anchors defined on the page
      reqanchors - list of anchors requesten for this page anchor->link*
      depth      - the number of clicks from the base urls this page to
                   find
      isinternal - whether the link is considered to be internal
      isyanked   - whether the link should be checked at all
      isfetched  - whether the lis is fetched already
      ispage     - whether the link represents a page
      mtime      - modification time (in seconds since the Epoch)
      size       - the size of this document
      mimetype   - the content-type of the document
      encoding   - the character set used in the document
      title      - the title of this document (unicode)
      author     - the author of this document (unicode)
      status     - the result of retreiving the document
      linkproblems - list of problems with retrieving the link
      pageproblems - list of problems in the parsed page
      redirectdepth - the number of this redirect (=0 not a redirect)

   Instances of this class should be made through a site instance
   by adding internal urls and calling crawl().
   """

    def __init__(self, site, url):
        """Creates an instance of the Link class and initializes the
        documented properties to some sensible value."""
        # store a reference to the site
        self.site = site
        # split the url in useful parts and store the parts
        (self.scheme, self.netloc, self.path, self.query) = \
          urlparse.urlsplit(url)[0:4]
        # store the url (without the fragment)
        url = urlparse.urlunsplit(
          (self.scheme, self.netloc, self.path, self.query, '') )
        self.url = url
        # ensure that we are not creating something that already exists
        assert not self.site.linkMap.has_key(url)
        # store the Link object in the linkMap
        self.site.linkMap[url] = self
        # deternmin the kind of url (internal or external)
        self.isinternal = self.site._is_internal(self)
        # check if the url is yanked
        self.isyanked = self.site._is_yanked(self)
        # initialize some properties
        self.parents = set()
        self.children = set()
        self.pagechildren = None
        self.embedded = set()
        self.anchors = set()
        self.reqanchors = {}
        self.depth = None
        self.isfetched = False
        self.ispage = False
        self.mtime = None
        self.size = None
        self.mimetype = None
        self.encoding = None
        self.title = None
        self.author = None
        self.status = None
        self.linkproblems = []
        self.pageproblems = []
        self.redirectdepth = 0
        self.redirectlist = None
        self._ischanged = False

    def __checkurl(self, url):
        """Check to see if the url is formatted properly, correct formatting
        if possible and log an error in the formatting to the current page."""
        # search for spaces in the url
        if _spacepattern.search(url):
            self.add_pageproblem('link contains unescaped spaces: %s' % url)
            # replace spaces by %20
            url = _spacepattern.sub('%20', url)
        # find anchor part
        try:
            # get the anchor
            anchor = _anchorpattern.search(url).group(1)
            # get link for url we link to
            child = self.site.get_link(url)
            # store anchor
            child.add_reqanchor(self, anchor)
        except AttributeError:
            # ignore problems lookup up anchor
            pass
        return url

    def __tolink(self, link):
        """Convert the link to a link object, either it is already a link,
        a link object is returned from the database or a new link is
        created. This returns None for empty strings."""
        # ignore if child is empty string
        if link == '' or link == u'':
            return None
        if type(link) is unicode and self.encoding:
            # convert url to binary if passed as unicode
            link = link.encode(self.encoding)
        # convert the url to a link object if we were called with a url
        if type(link) is unicode or type(link) is str:
            link = self.site.get_link(self.__checkurl(link))
        # re're done
        return link

    def add_child(self, child):
        """Add a link object to the child relation of this link.
        The reverse relation is also made."""
        # ignore children for external links
        if not self.isinternal:
            return
        # convert to link object
        child = self.__tolink(child)
        if child is None:
            return
        # add to children
        if child not in self.children:
            self.children.add(child)
            self._ischanged = True
        # add self to parents of child
        if self not in child.parents:
            child.parents.add(self)

    def add_embed(self, link):
        """Mark the given link object as used as an image on this page."""
        # ignore embeds for external links
        if not self.isinternal:
            return
        # convert to link object
        link = self.__tolink(link)
        if link is None:
            return
        # add to embedded
        if link not in self.embedded:
            self.embedded.add(link)
            self._ischanged = True
        # add self to parents of embed
        if self not in link.parents:
            link.parents.add(self)

    def add_anchor(self, anchor):
        """Indicate that this page contains the specified anchor."""
        # lowercase anchor
        anchor = anchor.lower()
        # add anchor
        if anchor in self.anchors:
            self.add_pageproblem(
              'anchor/id "%(anchor)s" defined multiple times'
              % { 'anchor':   anchor })
        else:
            self.anchors.add(anchor)
            self._ischanged = True

    def add_reqanchor(self, parent, anchor):
        """Indicate that the specified link contains a reference to the
        specified anchor. This can be checked later."""
        # lowercase anchor
        anchor = anchor.lower()
        # convert the url to a link object if we were called with a url
        parent = self.__tolink(parent)
        # add anchor
        if anchor in self.reqanchors:
            if parent not in self.reqanchors[anchor]:
                self.reqanchors[anchor].add(parent)
                self._ischanged = True
        else:
            self.reqanchors[anchor] = set([parent])
            self._ischanged = True

    def redirect(self, url):
        """Indicate that this link redirects to the specified url. Maximum
        redirect counting is done as well as loop detection."""
        # figure out depth and urls that have been visited in this
        # redirect list
        redirectdepth = 0
        redirectlist = set()
        for parent in self.parents:
            if parent.redirectdepth > redirectdepth:
                redirectdepth = parent.redirectdepth
                redirectlist = parent.redirectlist
        self.redirectdepth = redirectdepth + 1
        self.redirectlist = redirectlist
        self.redirectlist.add(self.url)
        # check depth
        if self.redirectdepth >= config.REDIRECT_DEPTH:
            self.add_linkproblem('too many redirects (%d)' % self.redirectdepth)
            return None
        # check for redirect to self
        url = self.__checkurl(url)
        if url == self.url:
            self.add_linkproblem('redirect same as source: %s' % url)
            return None
        # check for redirect loop
        if url in self.redirectlist:
            self.add_linkproblem('redirect loop %s' % url)
        # add child
        self.add_child(url)

    def add_linkproblem(self, problem):
        """Indicate that something went wrong while retreiving this link."""
        self.linkproblems.append(problem)
        self._ischanged = True

    def add_pageproblem(self, problem):
        """Indicate that something went wrong with parsing the document."""
        # only think about problems on internal pages
        if not self.isinternal:
            return
        # only include a single problem once (e.g. multiple anchors)
        if problem not in self.pageproblems:
            self.pageproblems.append(problem)
            self._ischanged = True

    def fetch(self):
        """Attempt to fetch the url (if isyanked is not True) and fill in link
        attributes (based on isinternal)."""
        # fully ignore links that should not be feteched
        if self.isyanked:
            debugio.info('  %s' % self.url)
            debugio.info('    ' + self.isyanked)
            return
        # see if we can import the proper module for this scheme
        schememodule = schemes.get_schememodule(self.scheme)
        if schememodule is None:
            self.isyanked = 'unsupported scheme (' + self.scheme + ')'
            self._ischanged = True
            debugio.info('  %s' % self.url)
            debugio.info('    ' + self.isyanked)
            return
        debugio.info('  %s' % self.url)
        content = schememodule.fetch(self, parsers.get_mimetypes())
        self.isfetched = True
        self._ischanged = True
        # skip parsing of content if we were returned nothing
        if content is None:
            return
        # find a parser for the content-type
        parsermodule = parsers.get_parsermodule(self.mimetype)
        if parsermodule is None:
            debugio.debug('crawler.Link.fetch(): unsupported content-type: %s' % self.mimetype)
            return
        # parse the content
        debugio.debug('crawler.Link.fetch(): parsing using %s' % parsermodule.__name__)
        parsermodule.parse(content, self)

    def follow_link(self, visited=set()):
        """If this link represents a redirect return the redirect target,
        otherwise return self. If this redirect does not find a referenced
        link None is returned."""
        # if this is not a redirect just return
        if self.redirectdepth == 0:
            return self
        # if we don't know where this redirects, return None
        if len(self.children) == 0:
            return None
        # the first (and only) child is the redirect target
        visited.add(self)
        # check for loops
        child = self.children.copy().pop()
        if child in visited:
            return None
        # check where we redirect to
        return child.follow_link(visited)

    def _pagechildren(self):
        """Determin the page children of this link, combining the children of
        embedded items and following redirects."""
        # if we already have pagechildren defined we're done
        if self.pagechildren is not None:
            return self.pagechildren
        self.pagechildren = set()
        # add my own children, following redirects
        for child in self.children:
            # follow redirects
            child = child.follow_link()
            # skip children we already have
            if child is None:
                continue
            # set depth of child if it is not already set
            if child.depth is None:
                child.depth = self.depth+1
            # add child pages to out pagechildren
            if child.ispage:
                self.pagechildren.add(child)
        # add my embedded element's children
        for embed in self.embedded:
            # set depth of embed if it is not already set
            if embed.depth is None:
                embed.depth = self.depth
            # merge in children of embeds
            self.pagechildren.update(embed._pagechildren())
        # return the results
        return self.pagechildren

    def set_encoding(self, encoding):
        """Set the encoding of the link doing some basic checks
        to see if the encoding is supported."""
        if self.encoding is None and encoding is not None:
            try:
                debugio.debug('crawler.Link.set_encoding("'+str(encoding)+'")')
                unicode('just some random text', encoding, 'replace')
                self.encoding = encoding
            except Exception:
                self.add_pageproblem('unknown encoding: ' + str(encoding))
