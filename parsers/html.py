
# html.py - parser functions for html content
#
# Copyright (C) 2005, 2006 Arthur de Jong
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

"""Parser functions for processing HTML content."""

import debugio
import HTMLParser
import urlparse
import re
import crawler
import htmlentitydefs

# the list of mimetypes this module should be able to handle
mimetypes = ('text/html', 'application/xhtml+xml', 'text/x-server-parsed-html')

# pattern for matching numeric html entities
_charentitypattern = re.compile('&#([0-9]{1,3});')

# pattern for matching all html entities
_entitypattern = re.compile('&(#[0-9]{1,6}|[a-zA-Z]{2,10});')

# pattern for matching spaces
_spacepattern = re.compile(' ')

# pattern for matching charset declaration for http-equiv tag
_charsetpattern = re.compile('charset=([^ ]*)', re.I)

# pattern for matching the encoding part of an xml declaration
_encodingpattern = re.compile('^xml .*encoding="([^"]*)"', re.I)

def htmlescape(txt, inattr=False):
    """HTML escape the given string and return an ASCII clean string with
    known entities and character entities for the other values.
    If the inattr parameter is set quotes and newlines will also be escaped."""
    # convert to unicode object
    if type(txt) is str:
        txt = unicode(txt, errors='replace')
    # the output string
    out = ''
    # loop over the characters of the string
    for c in txt:
        if c == '"':
            if inattr:
                out += '&%s;' % htmlentitydefs.codepoint2name[ord(c)]
            else:
                out += '"'
        elif htmlentitydefs.codepoint2name.has_key(ord(c)):
            out += '&%s;' % htmlentitydefs.codepoint2name[ord(c)]
        elif ord(c) > 126:
            out += '&#%d;'% ord(c)
        elif inattr and c == u'\n':
            out += '&#10;'
        else:
            out += c.encode('utf-8')
    return out

def _unescape_entity(match):
    """Helper function for htmlunescape().
    This funcion unescapes a html entity, it is passed to the sub()
    function."""
    if htmlentitydefs.name2codepoint.has_key(match.group(1)):
        # we have a named entity, return proper character
        return unichr(htmlentitydefs.name2codepoint[match.group(1)])
    elif match.group(1)[0] == '#':
        # we have a numeric entity, replace with proper character
        return unichr(int(match.group(1)[1:]))
    else:
        # we have something else, just keep the original
        return match.group(0)

def htmlunescape(txt):
    """This function unescapes a html encoded string.
    This function returns a unicode string."""
    # convert to unicode
    if type(txt) is str:
        txt = unicode(txt, errors='replace')
    # replace &name; and &#nn; refs with proper characters
    txt = _entitypattern.sub(_unescape_entity, txt)
    # we're done
    return txt

class _MyHTMLParser(HTMLParser.HTMLParser):
    """A simple subclass of HTMLParser.HTMLParser continuing after errors
    and gathering some information from the parsed content."""

    def __init__(self, link):
        """Inialize the menbers in which we collect data from parsing the
        document."""
        self.link = link
        self.collect = None
        self.base = None
        self.title = None
        self.author = None
        self.embedded = []
        self.children = []
        self.anchors = []
        self.errmsg = None
        self.errcount = 0
        HTMLParser.HTMLParser.__init__(self)

    def _location(self):
        """Return the current parser location as a string."""
        (lineno, offset) = self.getpos()
        if lineno is not None:
            msg = 'at line %d' % lineno
        else:
            msg = 'at unknown line'
        if offset is not None:
            msg += ', column %d' % (offset + 1)
        return msg

    def _cleanurl(self, url, what='link'):
        """Do some translations of url."""
        # check for spaces in urls
        # (characters are escaped in crawler.urlescape())
        if _spacepattern.search(url):
            self.link.add_pageproblem(
              what+' contains unescaped spaces: '+url+', '+self._location() )
        # replace &#nnn; entity refs with proper characters
        url = _charentitypattern.sub(lambda x:chr(int(x.group(1))), url)
        return crawler.urlescape(url)

    def error(self, message):
        """Override superclass' error() method to ignore errors."""
        # construct error message
        message += ', ' + self._location()
        # store error message
        debugio.debug('parsers.html._MyHTMLParser.error(): problem parsing html: '+message)
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
        except AssertionError:
            debugio.debug('parsers.html._MyHTMLParser.check_for_whole_start_tag(): caught assertion error')
            return None

    def handle_starttag(self, tag, attrs):
        """Handle start tags in html."""
        # turn attrs into hash
        attrs = dict(attrs)
        # <title>TITLE</title>
        if tag == 'title':
            self.collect = ''
        # <base href="URL">
        elif tag == 'base' and attrs.has_key('href'):
            self.base = self._cleanurl(attrs['href'])
        # <link rel="type" href="URL">
        elif tag == 'link' and attrs.has_key('rel') and attrs.has_key('href'):
            if attrs['rel'].lower() in ('stylesheet', 'alternate stylesheet', 'icon', 'shortcut icon'):
                self.embedded.append(self._cleanurl(attrs['href']))
        # <meta name="author" content="AUTHOR">
        elif tag == 'meta' and attrs.has_key('name') and attrs.has_key('content') and attrs['name'].lower() == 'author':
            if self.author is None:
                self.author = attrs['content']
        # <meta http-equiv="refresh" content="0;url=URL">
        elif tag == 'meta' and attrs.has_key('http-equiv') and attrs.has_key('content') and attrs['http-equiv'].lower() == 'refresh':
            pass # TODO: implement
        # <meta http-equiv="content-type" content="text/html; charset=utf-8" />
        elif tag == 'meta' and attrs.has_key('http-equiv') and attrs.has_key('content') and attrs['http-equiv'].lower() == 'content-type':
            try:
                self.link.set_encoding(_charsetpattern.search(attrs['content']).group(1))
            except AttributeError:
                # ignore cases where encoding is not set in header
                pass
        # <img src="url">
        elif tag == 'img' and attrs.has_key('src'):
            self.embedded.append(self._cleanurl(attrs['src']))
        # <a href="url" name="anchor" id="anchor">
        elif tag == 'a':
            # <a href="url">
            if attrs.has_key('href'):
                self.children.append(self._cleanurl(attrs['href']))
            # <a name="anchor">
            a_name = None
            if attrs.has_key('name'):
                a_name = self._cleanurl(attrs['name'], 'anchor')
            # <a id="anchor">
            a_id = None
            if attrs.has_key('id'):
                a_id = self._cleanurl(attrs['id'], 'anchor')
            # if both id and name are used they should be the same
            if a_id and a_name and a_id != a_name:
                # add problem
                self.link.add_pageproblem(
                  'anchors defined in name and id attributes do not match %(location)s'
                  % { 'location': self._location() })
            elif a_id == a_name:
                # ignore id if it's the same as name
                a_id = None
            # <a name="anchor">
            if a_name:
                if a_name in self.anchors:
                    self.link.add_pageproblem(
                      'anchor "%(anchor)s" defined again %(location)s'
                      % { 'anchor':   a_name,
                          'location': self._location() })
                else:
                    self.anchors.append(a_name)
            # <a id="anchor">
            if a_id:
                if a_id in self.anchors:
                    self.link.add_pageproblem(
                      'anchor "%(anchor)s" defined again %(location)s'
                      % { 'anchor':   a_id,
                          'location': self._location() })
                else:
                    self.anchors.append(a_id)
        # <frameset><frame src="url"...>...</frameset>
        elif tag == 'frame' and attrs.has_key('src'):
            self.embedded.append(self._cleanurl(attrs['src']))
        # <map><area href="url"...>...</map>
        elif tag == 'area' and attrs.has_key('href'):
            self.children.append(self._cleanurl(attrs['href']))
        # <applet code="url"...>
        elif tag == 'applet' and attrs.has_key('code'):
            self.embedded.append(self._cleanurl(attrs['code']))
        # <embed src="url"...>
        elif tag == 'embed' and attrs.has_key('src'):
            self.embedded.append(self._cleanurl(attrs['src']))
        # <embed><param name="movie" value="url"></embed>
        elif tag == 'param' and attrs.has_key('name') and attrs.has_key('value'):
            if attrs['name'].lower() == 'movie':
                self.embedded.append(self._cleanurl(attrs['value']))
        # <style>content</style>
        elif tag == 'style':
            self.collect = ''

    def handle_endtag(self, tag):
        """Handle end tags in html."""
        if tag == 'title' and self.title is None:
            self.title = self.collect
            self.collect = None
        elif tag == 'style' and self.collect is not None:
            # delegate handling of inline css to css module
            import parsers.css
            parsers.css.parse(self.collect, self.link)

    def handle_data(self, data):
        """Collect data if we were collecting data."""
        if self.collect is not None:
            self.collect += data

    def handle_charref(self, name):
        """Handle character references (e.g. &#65;) by passing the data to
        handle_data()."""
        self.handle_data('&#'+name+';')
        # TODO: do not pass ; if plain text does not contain it?

    def handle_entityref(self, name):
        """Handle entity references (e.g. &eacute;) by passing the data to
        handle_data()."""
        self.handle_data('&'+name+';')
        # TODO: do not pass ; if plain text does not contain it?

    def handle_pi(self, data):
        """Handle xml declaration."""
        # find character encoding from declaration
        try:
            self.link.set_encoding(_encodingpattern.search(data).group(1))
        except AttributeError:
            pass

def _maketxt(txt, encoding):
    """Return an unicode text of the specified string do correct character
    conversions and replacing html entities with normal characters."""
    # try to decode with the given encoding
    if encoding:
        try:
            return htmlunescape(unicode(txt, encoding, 'replace'))
        except (LookupError, TypeError, ValueError), e:
            debugio.warn('page has unknown encoding: %s' % str(encoding))
    # fall back to locale's encoding
    return htmlunescape(unicode(txt, errors='replace'))

def parse(content, link):
    """Parse the specified content and extract an url list, a list of images a
    title and an author. The content is assumed to contain HMTL."""
    # create parser and feed it the content
    parser = _MyHTMLParser(link)
    try:
        parser.feed(content)
        parser.close()
    except Exception, e:
        # ignore (but log) all errors
        debugio.debug('parsers.html.parse(): caught exception: '+str(e))
    # check for parser errors
    if parser.errmsg is not None:
        debugio.debug('parsers.html.parse(): problem parsing html: '+parser.errmsg)
        link.add_pageproblem('problem parsing html: %s' % parser.errmsg)
    # dump encoding
    debugio.debug('parsers.html.parse(): html encoding: %s' % str(link.encoding))
    # flag that the link contains a valid page
    link.ispage = True
    # save the title
    if parser.title is not None:
        link.title = _maketxt(parser.title, link.encoding).strip()
    # save the author
    if parser.author is not None:
        link.author = _maketxt(parser.author, link.encoding).strip()
    # figure out the base of the document (for building the other urls)
    base = link.url
    if parser.base is not None:
        base = parser.base
    # list embedded and children
    for embed in parser.embedded:
        if embed:
            link.add_embed(urlparse.urljoin(base, embed))
    for child in parser.children:
        if child:
            link.add_child(urlparse.urljoin(base, child))
    # list anchors
    for anchor in parser.anchors:
        if anchor:
            link.add_anchor(anchor)
