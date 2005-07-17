
# myUrlLib.py - generic library for handling urls and links
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk) <marduk@python.net>
# Copyright (C) 2002 Mike Meyer <mwm@mired.org>
# Copyright (C) 2005 Arthur de Jong <arthur@tiefighter.et.tudelft.nl>
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

"""Generic library for handling urls and links"""

robot_parsers={}
compiled_ex = []
compiled_yanked = []

import config
from urllib import *
import httplib
import robotparser
import string
# The following is to help sgmllib parse DOS/Windows text files
string.whitespace = string.whitespace + '\012\015'
import time
import re
import stat
import debugio
import sys
import socket
import types
import urlparse
import schemes

def get_robots(location):
    global robot_parsers
    debugio.info('  getting robots.txt for %s' % location)
    rp=robotparser.RobotFileParser()
    try:
        rp.set_url('http://' + location + '/robots.txt')
        rp.read()
        robot_parsers[location]=rp
    except TypeError:
        pass

def can_fetch(location, url):
    """Return true if url is allowed at location, else return 0"""
    if robot_parsers.has_key(location):
        return robot_parsers[location].can_fetch('webcheck',url)
    return 1

def urlclean(url,parent=None):
    """Return a cleaned up absolute url, possibly using parent as a base.
    This function strips fragment (#...) from the url."""
    # make an absolute url
    if parent is not None:
        url=urlparse.urljoin(parent,url)
    # remove any fragments
    return urlparse.urldefrag(url)[0]

############################################################################
class Link:
    """ my class of url's which includes parents, HTTP status number, and
        a list of urls in that link urls.
    """

    linkMap = {}
    badLinks = []
    notChecked = []
    images = {}
    base=""

    # This is a static variable to indicate if the config.EXCLUDED urls have been
    # compiled as regular expressions.
    re_compiled = 0

    def __init__(self,url,parent):
        self.init()

        debugio.debug('  parent = ' + str(parent))

        parsed = urlparse.urlparse(url)
        self.scheme = parsed[0]
        location = parsed[1]

        if parent not in self.parents:
            if parent: self.parents.append(parent)

        self.url = url
        Link.linkMap[self.url]=self

        # see if we can import module for this scheme
        self.schememodule=schemes.get_schememodule(self.scheme)
        if self.schememodule is None:
            debugio.info("  unsupported scheme ("+self.scheme+")")
            self.status="Not Checked"
            self.external=True
            Link.notChecked.append(self.url)
            Link.linkMap[self.url]=self
            return

        if (parent is None):
            Link.base=self.url
            debugio.info('  base: %s' % Link.base)
            if self.scheme == 'http':
                base_location = parsed[1]
                if base_location not in config.HOSTS:
                    config.HOSTS.append(base_location)
                if not robot_parsers.has_key(location):
                    try:
                        get_robots(location)
                    except IOError:
                        pass

        # see if robots.txt will let us in
        if self.scheme == 'http':
            if not can_fetch(location, url):
                debugio.info('  robot restriced')
                self.status = 'Not Checked'
                self.message = 'Robot Restricted'
                Link.notChecked.append(url)
                return

        try:
            self.schememodule.get_info(self)
            if (self.url not in Link.badLinks) and (self.type == 'text/html'):
                page = self.schememodule.get_document(self)
                self._handleHTML(self.url, page)
        except IOError, data:
            self.set_bad_link(url,str(data.errno) + ': ' + str(data.strerror))
            return
        except socket.error, data:
            if type(data) is types.StringType:
                self.set_bad_link(url, data)
            elif type(data) is types.TupleType:
                errno, string = data
                self.set_bad_link(url,str(errno) + ': ' + string)
            else:
                self.set_bad_link(url,str(data))
        except KeyboardInterrupt:
            raise KeyboardInterrupt
#         except:
#             self.set_bad_link(url,"Error: Malformed url?")
#             debugio.debug("  %s: %s" % (sys.exc_type, sys.exc_value))
#             return

    def explore_children(self):
        for child in self.children:
            if not Link.linkMap.has_key(child):
                if config.WAIT_BETWEEN_REQUESTS > 0:
                    debugio.debug('sleeping %s seconds' %  config.WAIT_BETWEEN_REQUESTS)
                    time.sleep(config.WAIT_BETWEEN_REQUESTS)
                debugio.debug("adding url: %s" % child)
                if is_yanked(child):
                    Link.linkMap[child]=ExternalLink(child,self.url,1)
                elif is_external(child) or is_excluded(child):
                    Link.linkMap[child]=ExternalLink(child,self.url)
                else:
                    Link.linkMap[child]=Link(child,self.url)
            elif self.url not in Link.linkMap[child].parents:
                Link.linkMap[child].parents.append(self.url)
        return # __init__

    def init(self):
        """ initialize some variables """
        self.mtime = None
        self.scheme = None
        self.headers = None
        self.parents= []
        self.children = []
        self.status = None
        self.title = None
        self.external = 0
        self.html = 0
        self.size = 0
        self.totalSize = 0
        self.author = None

    def __repr__(self):
        return self.url

    def set_bad_link(self,url,status):
        """ flags the link as bad """
        debugio.info('  ' + str(status))
        self.status = str(status)
        self.url=url
        Link.linkMap[self.url]=self
        Link.badLinks.append(self.url)

    def _handleHTML(self,url,htmlfile):
        """examines and html file and updates the Link object"""
        # parse the html content
        import parsers.html
        (anchorlist, imagelist, title, author) = parsers.html.parse(htmlfile)
        debugio.info('  title: %s' % str(title))
        for child in anchorlist:
            child=urlclean(child,url)
            if child not in self.children:
                self.children.append(child)
        self.totalSize = self.size
        self.title = title
        self.author = author
        self.html = 1
        # get image list
        for image in imagelist:
            image=urlclean(image,url)
            if image not in Link.images.keys():
                debugio.info('  adding image: %s' % image)
                Link.images[image] = Image(image, self.url)
            self.totalSize = self.totalSize + int(Link.images[image].size)
        if not self.external:
            self.explore_children()


class ExternalLink(Link):
    """ this class is just like Link, but it does not explore it's children """

    def __init__(self,url,parent,yanked=0):

        if config.AVOID_EXTERNAL_LINKS or yanked:
            self.init()
            self.url = url
            Link.linkMap[self.url]=self
            self.status="Not Checked"
            self.external=1
            debugio.info('  not checked')
            if yanked: debugio.info('  yanked')
            if parent not in self.parents:
                if parent: self.parents.append(parent)
            Link.notChecked.append(url)
            return
        Link.__init__(self,url,parent)
        self.external=1


    def _handleHTML(self,url,htmlfile):
        # ignore links and images, but use the title
        import parsers.html
        self.title = parsers.html.parse(htmlfile)[2]
        debugio.info('  title: %s' % str(self.title))
        self.children=[]

class Image(Link):
    """ This class is just like link, but different :-)"""
    def __init__(self, url, parent):
        #self.init()
        Link.__init__(self, url, parent)

    def _handleHTML(self,url,htmlfile):
        """Don't handle HTML, this is an image"""
        self.set_bad_link(url,"HTML file used in IMG tag?")
        return

def is_external(url):
    """ returns true if url is an external link """
    parsed = urlparse.urlparse(url)
    scheme = parsed[0]
    location = parsed[1]
    if (location not in config.HOSTS) and (scheme in ['http','ftp']):
        return 1
    if config.BASE_URLS_ONLY and (Link.base!=url[:len(Link.base)]):
        return 1
    return 0

def compile_re():
    """Compile EXCLUDED urls and set flag"""
    global compiled_ex
    for i in config.EXCLUDED_URLS:
        debugio.debug('compiling %s' % i)
        compiled_ex.append(re.compile(i,re.IGNORECASE))
    for i in config.YANKED_URLS:
        debugio.debug('compiling %s' % i)
        compiled_yanked.append(re.compile(i,re.IGNORECASE))
    Link.re_compiled = 1

def is_excluded(url):
    """ Returns true if url is part of the EXCLUDED_URLS list """
    if not Link.re_compiled:
        compile_re()
    for x in compiled_ex:
        if x.search(url) is not None:
            return 1
    return 0

def is_yanked(url):
    """ Returns true if url is part of YANKED_URLS list"""
    if not Link.re_compiled:
        compile_re()
    for x in compiled_yanked:
        if x.search(url) is not None:
            return 1
    return 0
