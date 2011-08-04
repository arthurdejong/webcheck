
# html.py - parser functions for html content
#
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

"""Parser functions for processing HTML content. This a front-end
module that tries to load the BeatifulSoup parser first and falls
back to loading the legacy HTMLParser parser."""

import debugio
import re
import htmlentitydefs
import config

# the list of mimetypes this module should be able to handle
mimetypes = ('text/html', 'application/xhtml+xml', 'text/x-server-parsed-html')

# pattern for matching all html entities
_entitypattern = re.compile('&(#[0-9]{1,6}|[a-zA-Z]{2,10});')

def htmlescape(txt, inattr=False):
    """HTML escape the given string and return an ASCII clean string with
    known entities and character entities for the other values.
    If the inattr parameter is set quotes and newlines will also be escaped."""
    # check for empty string
    if not txt:
        return u''
    # convert to unicode object
    if not isinstance(txt, unicode):
        txt = unicode(txt)
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
    # check for empty string
    if not txt:
        return u''
    # convert to unicode
    if not isinstance(txt, unicode):
        txt = unicode(txt, errors='replace')
    # replace &name; and &#nn; refs with proper characters
    txt = _entitypattern.sub(_unescape_entity, txt)
    # we're done
    return txt

def _parsefunction(content, link):
    # we find a suitable parse function
    global _parsefunction
    try:
        # try BeautifulSoup parser first
        import parsers.html.beautifulsoup
        debugio.debug('parsers.html.parse(): the BeautifulSoup parser is ok')
        _parsefunction = parsers.html.beautifulsoup.parse
    except ImportError:
        # fall back to legacy HTMLParser parser
        debugio.warn('falling back to the legacy HTML parser, consider installing BeautifulSoup')
        import parsers.html.htmlparser
        _parsefunction = parsers.html.htmlparser.parse
    # call the actual parse function
    _parsefunction(content, link)

def parse(content, link):
    """Parse the specified content and extract an url list, a list of images a
    title and an author. The content is assumed to contain HMTL."""
    # call the normal parse function
    _parsefunction(content, link)
    # call the tidy parse function
    if config.TIDY_OPTIONS:
        try:
            import calltidy
            debugio.debug('parsers.html.parse(): the Tidy parser is ok')
            calltidy.parse(content, link)
        except ImportError:
            debugio.warn('tidy library (python-utidylib) is unavailable')
            # remove config to only try once
            config.TIDY_OPTIONS = None
