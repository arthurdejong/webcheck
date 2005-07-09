
# html.py - parser functions for html content
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

"""Parser functions for processing HTML content."""

import htmllib
import string
import debugio
import formatter
import sgmllib

# TODO: switch to using HTMLParser (not from htmllib)

class _MyHTMLParser(htmllib.HTMLParser):

    def __init__(self,formatter):
        self.imagelist = []
        self.title = None
        self.author = None
        self.base = None
        htmllib.HTMLParser.__init__(self,formatter)

    # override handle_image()
    def handle_image(self,src,alt,*stuff):
        if src not in self.imagelist:
            self.imagelist.append(src)

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
                    self.author = fields['content']

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

def parse(content):
    """Parse the specified content and extract an url list, a list of images a
    title and an author. The content is assumed to contain HMTL."""
    # parse the file
    parser = _MyHTMLParser(formatter.NullFormatter())
    try:
        parser.feed(content)
        parser.close()
    except sgmllib.SGMLParseError, e:
        debugio.warn('problem parsing html: %s' % (str(e)))
        #FIXME: flag a problem with this link
    # generate list of links
    urllist = []
    for anchor in parser.anchorlist:
        # create absolute url based on <base> tag
        if parser.base is not None:
            anchor = urllib.join(parser.base,anchor)
        # add anchor to urllist
        if anchor not in urllist:
            urllist.append(anchor)
    # generate list of images
    imagelist = []
    for image in parser.imagelist:
        # create absolute url based on <base> tag
        if parser.base is not None:
            image = urllib.join(parser.base,image)
        # add image to imageslist
        if image not in imagelist:
            imagelist.append(image)
    # return the data
    return (urllist, imagelist, parser.title, parser.author)
