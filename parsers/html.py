
# html.py - parser functions for html content
#
# Copyright (C) 2005 Arthur de Jong
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

import config
import debugio
import HTMLParser
import urlparse

# the list of mimetypes this module should be able to handle
mimetypes = ('text/html', 'application/xhtml+xml', 'text/x-server-parsed-html')

class _MyHTMLParser(HTMLParser.HTMLParser):
    """A simple subclass of HTMLParser.HTMLParser continuing after errors
    and gathering some information from the parsed content."""

    def __init__(self):
        """Inialize the menbers in which we collect data from parsing the
        document."""
        self.collect = None
        self.base = None
        self.title = None
        self.author = None
        self.embedded = []
        self.children = []
        self.errmsg = None
        self.errcount = 0
        HTMLParser.HTMLParser.__init__(self)

    def error(self, message):
        """Override superclass' error() method to ignore errors."""
        # construct error message
        (lineno, offset) = self.getpos()
        if lineno is not None:
            message += ", at line %d" % lineno
        if offset is not None:
            message += ", column %d" % (offset + 1)
        # store error message
        debugio.debug("parsers.html._MyHTMLParser.error(): problem parsing html: "+message)
        if self.errmsg is None:
            self.errmsg = message
        # increment error count
        self.errcount += 1
        if self.errcount > 10:
            raise HTMLParser.HTMLParseError(message, self.getpos())

    def check_for_whole_start_tag(self, i):
        """Override to catch assertion exception."""
        try:
            return HTMLParser.HTMLParser.check_for_whole_start_tag(self, i)
        except AssertionError, e:
            debugio.debug("parsers.html._MyHTMLParser.check_for_whole_start_tag(): caugt assertion error")

    def handle_starttag(self, tag, attrs):
        """Handle start tags in html."""
        # turn attrs into hash
        attrs=dict(attrs)
        # <title>content</title>
        if tag == "title":
            self.collect = ""
        # <base href="url">
        elif tag == "base" and attrs.has_key("href"):
            self.base = attrs["href"]
        # <link rel="type" href="url">
        elif tag == "link" and attrs.has_key("rel") and attrs.has_key("href"):
            if attrs["rel"].lower() in ("stylesheet", "alternate stylesheet", "icon", "shortcut icon"):
                self.embedded.append(attrs["href"])
        # <meta name="author" content="...">
        elif tag == "meta" and attrs.has_key("name") and attrs.has_key("content") and attrs["name"].lower() == "author":
            if self.author is None:
                self.author = attrs["content"]
        # <meta http-equiv="refresh" content="0;url=http://ch.tudelft.nl/~arthur/">
        elif tag == "meta" and attrs.has_key("http-equiv") and attrs.has_key("content") and attrs["http-equiv"].lower() == "refresh":
            pass # TODO: implement
        # <img src="url">
        elif tag == "img" and attrs.has_key("src"):
            self.embedded.append(attrs["src"])
        # <a href="url">
        elif tag == "a" and attrs.has_key("href"):
            self.children.append(attrs["href"])
        # <frameset><frame src="url"...>...</frameset>
        elif tag == "frame" and attrs.has_key("src"):
            self.embedded.append(attrs["src"])
        # <map><area href="url"...>...</map>
        elif tag == "area" and attrs.has_key("href"):
            self.children.append(attrs["href"])
        # <applet code="url"...>
        elif tag == "applet" and attrs.has_key("code"):
            self.embedded.append(attrs["code"])
        # <embed src="url"...>
        elif tag == "embed" and attrs.has_key("src"):
            self.embedded.append(attrs["src"])
        # <embed><param name="movie" value="url"></embed>
        elif tag == "param" and attrs.has_key("name") and attrs.has_key("value"):
            if attrs["name"].lower() == "movie":
                self.embedded.append(attrs["value"])

    def handle_endtag(self, tag):
        """Handle end tags in html."""
        if tag == 'title' and self.title is None:
            self.title = self.collect
            self.collect = None

    def handle_data(self, data):
        """Collect data if we were collecting data."""
        if self.collect is not None:
            self.collect += data

def parse(content, link):
    """Parse the specified content and extract an url list, a list of images a
    title and an author. The content is assumed to contain HMTL."""
    # create parser and feed it the content
    parser = _MyHTMLParser()
    try:
        parser.feed(content)
        parser.close()
    except HTMLParser.HTMLParseError:
        pass
    # check for parser errors
    if parser.errmsg is not None:
        debugio.debug("parsers.html.parse(): problem parsing html: "+parser.errmsg)
        link.add_problem('problem parsing html: %s' % parser.errmsg)
        pass
    # flag that the link contains a valid page
    link.ispage = True
    # save the title
    if parser.title is not None:
        link.title = parser.title
    # save the author
    if parser.author is not None:
        link.author = parser.author
    # figure out the base of the document (for building the other urls)
    base = link.url
    if parser.base is not None:
        base = parser.base
    # list embedded and children
    for embed in parser.embedded:
        link.add_embed(urlparse.urljoin(base,embed))
    for child in parser.children:
        link.add_child(urlparse.urljoin(base,child))
