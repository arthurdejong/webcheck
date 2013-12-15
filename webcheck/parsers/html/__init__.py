
# html.py - parser functions for html content
#
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

"""Parser functions for processing HTML content. This a front-end
module that tries to load the BeatifulSoup parser first and falls
back to loading the legacy HTMLParser parser."""

import htmlentitydefs
import logging
import re

from webcheck import config


logger = logging.getLogger(__name__)


# the list of mimetypes this module should be able to handle
mimetypes = ('text/html', 'application/xhtml+xml', 'text/x-server-parsed-html')

# pattern for matching all html entities
_entitypattern = re.compile('&(#[0-9]{1,6}|[a-zA-Z]{2,10});')


def _unescape_entity(match):
    """Helper function for htmlunescape().
    This funcion unescapes a html entity, it is passed to the sub()
    function."""
    if match.group(1) in htmlentitydefs.name2codepoint:
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
        import webcheck.parsers.html.beautifulsoup
        logger.debug('the BeautifulSoup parser is ok')
        _parsefunction = webcheck.parsers.html.beautifulsoup.parse
    except ImportError:
        # fall back to legacy HTMLParser parser
        logger.warn('falling back to the legacy HTML parser, '
                    'consider installing BeautifulSoup')
        import webcheck.parsers.html.htmlparser
        _parsefunction = webcheck.parsers.html.htmlparser.parse
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
            import webcheck.parsers.html.calltidy
            webcheck.parsers.html.calltidy.parse(content, link)
        except ImportError:
            logger.warn('tidy library (python-utidylib) is unavailable')
            # remove config to only try once
            config.TIDY_OPTIONS = None
