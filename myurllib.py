
# myurllib.py - general purpose URL handling library
#
# Copyright (C) 2007, 2011 Arthur de Jong
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

import urlparse
import re
import urllib

# this is a workaround for Python 2.3
try:
    set
except NameError:
    from sets import Set as set

# The way I read RFC3986 (especially sections 3.3 and 6.2) is that these
# are all separate and valid URLs that point to the same resource.
#
# In section 6.2.2.3 only the removal of "." and ".." in paths is
# mentioned although 6.2.3 does leave some room for other normalisation.

# pattern for matching URL-encoded characters
_urlencpattern = re.compile('(%[0-9a-fA-F]{2})')

# characters that should be unescaped in URLs
_okurlchars = set('-.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
                  '_abcdefghijklmnopqrstuvwxyz~')

# pattern for matching characters that should be escaped
_urlprobpattern = re.compile('([^-;/?:@&=+$,%#.0123456789' \
                             'ABCDEFGHIJKLMNOPQRSTUVWXYZ_' \
                             'abcdefghijklmnopqrstuvwxyz~])')

# pattern for double slashes
_doubleslashpattern = re.compile('//+')

# pattern for leading dots
_leadingdotpattern = re.compile('^(/\.\.)*')


def _unescape_printable(match):
    """Helper function for _normalize_escapes() to perform the expansion of
    html entity refs that are normal printable (but not reserver)
    characters."""
    # unescape the character
    r = chr(int(match.group(1)[1:3], 16))
    if r in _okurlchars:
        return r
    # transform remaining escapes to uppercase
    return match.group(1).upper()


def _normalize_escapes(url):
    """Ensure that escaping in the url is consistent. Any reserved characters
    are left alone. Any characters that are printable but are escaped are
    unescaped. Any non-printable characters are escaped."""
    # url decode any printable normal characters (this leaves us with a string
    # with as much stuff unquoted as # possible)
    url = _urlencpattern.sub(_unescape_printable, url)
    # url encode any nonprintable or problematic characters (but not reserved
    # characters) so we're left with a string with everything that needs to be
    # quoted as such
    url = _urlprobpattern.sub(lambda x: '%%%02X' % ord(x.group(1)), url)
    return url


def _urlclean(url):
    """Clean the url of uneccesary parts."""
    # make escaping consistent
    url = _normalize_escapes(url)
    # split the url in useful parts
    (scheme, netloc, path, query, fragment) = urlparse.urlsplit(url)
    # remove any leading /../ parts
    if scheme in ('http', 'https'):
        path = _leadingdotpattern.sub('', path)
    if scheme in ('http', 'https', 'ftp'):
        # http(s) urls should have a non-empty path
        if path == '':
            path = '/'
        # make hostname lower case
        (userpass, hostport) = urllib.splituser(netloc)
        (host, port) = urllib.splitport(hostport)
        # remove default port
        if scheme == 'http' and str(port) == '80':
            hostport = host
        elif scheme == 'https' and str(port) == '443':
            hostport = host
        netloc = hostport.lower()
        # trim trailing :
        if netloc[-1:] == ':':
            netloc = netloc[:-1]
        if userpass is not None:
            netloc = userpass + '@' + netloc
    # get rid of double slashes in some paths
    if scheme == 'file':
        path = _doubleslashpattern.sub('/', path)
    # put the url back together again
    return urlparse.urlunsplit((scheme, netloc, path, query, fragment))


def normalizeurl(url):
    """Return a normalized URL."""
    return _urlclean(url)
