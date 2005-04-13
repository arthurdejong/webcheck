
# myUrlLib.py - generic library for handling urls and links
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk) <marduk@python.net>
# Copyright (C) 2002 Mike Meyer <mwm@mired.org>
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
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

"""Generic library for handling urls and links"""

config = None
robot_parsers={}
SECS_PER_DAY=60*60*24
compiled_ex = []
compiled_yanked = []

from urllib import *
import htmllib
import httplib
import robotparser
import string
# The following is to help sgmllib parse DOS/Windows text files
string.whitespace = string.whitespace + '\012\015'
import time
import re
import stat
import htmlparse
import debugio
import sys
import socket
import types

def get_robots(location):
    global robot_parsers
    debugio.write('  Getting robots.txt for %s' % location)
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
        return robot_parsers[location].can_fetch('Webcheck',url)
    return 1

############################################################################
class Link:
    """ my class of url's which includes parents, HTTP status number, and
        a list of URL's in that link urls.
    """

    linkList = {}
    badLinks = []
    notChecked = []
    images = {}
    baseurl = ""
    base=""

    # This is a static variable to indicate if the config.EXCLUDED urls have been
    # compiled as regular expressions.
    re_compiled = 0

    def __init__(self,url,parent):
        self.init()

        debugio.write('  parent = ' + str(parent),2)
        from urlparse import urlparse

        parsed = urlparse(url)
        self.scheme = parsed[0]
        location = parsed[1]

        if parent not in self.parents:
            if parent: self.parents.append(parent)
            
        self.URL = url
        Link.linkList[self.URL]=self

        # see if we can import module for this scheme
        self.schememodule=get_schememodule(self.scheme)
        if self.schememodule is None:
            debugio.write("  unsupported scheme ("+self.scheme+")")
            self.status="Not Checked"
            self.external=True
            Link.notChecked.append(self.URL)
            Link.linkList[self.URL]=self
            return

        if (parent is None):
            Link.baseurl=self.URL
            if hasattr(self.URL, 'rfind'):
                Link.base=self.URL[:self.URL.rfind('/')+1]
            else:
                Link.base=self.URL[:string.rfind(self.URL,'/')+1]
            if Link.base[-2:] == '//': Link.base = self.URL
            debugio.write('  base: %s' % Link.base)
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
                debugio.write('  Robot Restriced')
                self.status = 'Not Checked'
                self.message = 'Robot Restricted'
                Link.notChecked.append(url)
                return

        try:
            self.schememodule.init(self, url, parent)
            if (self.URL not in Link.badLinks) and (self.type == 'text/html'):
                page = self.schememodule.get_document(self.URL)
                self._handleHTML(self.URL, page)
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
        except:
            self.set_bad_link(url,"Error: Malformed URL?")
            debugio.write("  %s: %s" % (sys.exc_type, sys.exc_value),3)
            return
        
    def explore_children(self):
        for child in self.children:
            if not Link.linkList.has_key(child):
                if config.WAIT_BETWEEN_REQUESTS > 0:
                    debugio.write('sleeping %s seconds' %  config.WAIT_BETWEEN_REQUESTS)
                    time.sleep(config.WAIT_BETWEEN_REQUESTS)
                debugio.write("adding url: %s" % child)
                if is_yanked(child):
                    Link.linkList[child]=ExternalLink(child,self.URL,1)
                elif is_external(child) or is_excluded(child):
                    Link.linkList[child]=ExternalLink(child,self.URL)
                else:
                    Link.linkList[child]=Link(child,self.URL)
            elif self.URL not in Link.linkList[child].parents:
                Link.linkList[child].parents.append(self.URL)
        return # __init__

    def init(self):
        """ initialize some variables """
        self.age = None
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
        return self.URL

    def set_bad_link(self,url,status):
        """ flags the link as bad """
        debugio.write('  ' + str(status))
        self.status = str(status)
        self.URL=url
        Link.linkList[self.URL]=self
        Link.badLinks.append(self.URL)

    def _handleHTML(self,url,htmlfile):
        """examines and html file and updates the Link object"""
        # get anchorlist
        (anchorlist, imagelist, title, author) = htmlparse.pageLinks(url,htmlfile)

        debugio.write('  title: %s' % str(title))
        for child in anchorlist:
            if child not in self.children:
                self.children.append(child)
                    
        self.totalSize = self.size
        self.title = title
        self.author = author
        self.html = 1
        # get image list
        for image in imagelist:
            if image not in Link.images.keys():
                debugio.write('  adding image: %s' % image)
                Link.images[image] = Image(image, self.URL)
            self.totalSize = self.totalSize + int(Link.images[image].size)
        if not self.external: self.explore_children()
        return



class ExternalLink(Link):
    """ this class is just like Link, but it does not explore it's children """
    
    def __init__(self,url,parent,yanked=0):

        if config.AVOID_EXTERNAL_LINKS or yanked:
            self.init()
            self.status="Not Checked"
            self.external=1
            debugio.write('  Not checked')
            if yanked: debugio.write('  Yanked')
            if parent not in self.parents:
                if parent: self.parents.append(parent)
            Link.notChecked.append(url)
            return
        Link.__init__(self,url,parent)
        self.external=1


    def _handleHTML(self,url,htmlfile):
        # ignore links and images, but use the title
        self.title = htmlparse.pageLinks(url,htmlfile)[2]
        debugio.write('  title: %s' % str(self.title))
        self.children=[]

class Image(Link):
    """ This class is just like link, but different :-)"""
    def __init__(self, url, parent):
        #self.init()
        Link.__init__(self, url, parent)
        #self.age = getAge(self)

    def _handleHTML(self,url,htmlfile):
        """Don't handle HTML, this is an image"""
        self.set_bad_link(url,"HTML file used in IMG tag?")
        return

def is_external(url):
    """ returns true if url is an external link """
    from urlparse import urlparse
    parsed = urlparse(url)
    scheme = parsed[0]
    location = parsed[1]
    if (location not in config.HOSTS) and (scheme in ['http','ftp']):
        return 1
    if config.BASE_URLS_ONLY and (Link.base!=url[:len(Link.base)]):
        return 1
    return 0

def compile_re():
    """Compile EXCLUDED URLSs and set flag"""
    global compiled_ex
    for i in config.EXCLUDED_URLS:
        debugio.write('compiling %s' % i,3)
        compiled_ex.append(re.compile(i,re.IGNORECASE))
    for i in config.YANKED_URLS:
        debugio.write('compiling %s' % i,3)
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

# a map of schemes to modules
schememodules={}

def get_schememodule(scheme):
    """look up the correct module for the specified scheme"""
    if not schememodules.has_key(scheme):
        try:
            schememodules[scheme]=__import__('schemes.'+scheme,globals(),locals(),[scheme])
        except ImportError:
            schememodules[scheme]=None
    return schememodules[scheme]
