# Copyright (C) 1998,1999  marduk <marduk@python.net>
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

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


"""Utilites for parsing HTML and urls"""

import htmllib
import string
import debugio
from urlparse import urlparse, urljoin, urlunparse
from formatter import NullFormatter

def urlformat(url,parent=None):
    """ returns a formatted version of URL, which, adds trailing '/'s, if 
    necessary, deletes fragmentation identifiers '#' and expands partial url's 
    based on parent"""
    
    method=urlparse(url)[0]
    if (method=='') and (parent != None):
        url=urljoin(parent,url)
        #url=basejoin(parent,url)
    parsedlist = list(urlparse(url))
    parsedlist[5]='' # remove fragment
    # parsedlist[4]='' # remove query string
    url = urlunparse(tuple(parsedlist))
    return url


class MyHTMLParser(htmllib.HTMLParser):
    
    def __init__(self,formatter):
        self.imagelist = []
        self.title = None
        self.author = None
        self.base = None
        htmllib.HTMLParser.__init__(self,formatter)
        
    # override handle_image() 
    def handle_image(self,src,alt,*stuff):
        if src not in self.imagelist: self.imagelist.append(src)

    def do_frame(self,attrs):
        for name, val in attrs:
            if name=="src":
                self.anchorlist.append(val)

    def save_bgn(self):
        self.savedata = ''
        

    def save_end(self):
        data = self.savedata
        self.savedata = None
        return data

    def start_title(self, attrs):
        self.save_bgn()

    def end_title(self):
        #if not self.savedata:
        #    self.title = None
        #    return
        self.title = string.join(string.split(self.save_end()))

    def do_meta(self,attrs):
        fields={}
        for name, value in attrs:
            fields[name]=value
        if fields.has_key('name'):
            if string.lower(fields['name']) == 'author':
                if fields.has_key('content'):
                    author = fields['content']
                    self.author = author
                    debugio.write('\tauthor: ' + author)

    # stylesheet links
    def do_link(self,attrs):
        for name, val in attrs:
            if name=="href":
                if val not in self.anchorlist:
                    self.anchorlist.append(val)

    # <AREA> for client-side image maps
    def do_area(self,attrs):
        for name, val in attrs:
            if name=="href":
                if val not in self.anchorlist:
                    self.anchorlist.append(val)

    def do_base(self,attrs):
        for name,val in attrs:
            if name=="href":
                self.base = val

def pageLinks(url,page):
    """ returns a list of all the url's in a page.  page should be a file object
    Partial urls will be expanded using <url> parameter unless the page contains
    the <BASE HREF=> tag."""

    parser = MyHTMLParser(NullFormatter())
    parser.feed(page)
    parser.close()
    urllist = []
    imagelist = []
        
    title = parser.title
    author = parser.author
    if parser.base is not None:
        parent = parser.base
    else:
        parent = url
    for anchor in parser.anchorlist:
        anchor=urlformat(anchor,parent)
        if anchor not in urllist: urllist.append(anchor)
        
    for image in parser.imagelist:
        image=urlformat(image,parent)
        if image not in imagelist: imagelist.append(image)

    return (urllist, imagelist, title, author)
