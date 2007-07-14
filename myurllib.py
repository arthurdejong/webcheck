
# myurllib.py - general purpose URL handling library
#
# Copyright (C) 2007 Arthur de Jong
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


# The way I read RFC3986 (especially sections 3.3 and 6.2) is that these
# are all separate and valid URLs that point to the same resource.
# 
# In section 6.2.2.3 only the removal of "." and ".." in paths is
# mentioned although 6.2.3 does leave some room for other normalisation.

# pattern for matching url encoded characters
_urlencpattern = re.compile('(%[0-9a-fA-F]{2})')

# pattern for double slashes
_doubleslashpattern = re.compile('//+')

# characters that should not be escaped in urls
_reservedurlchars = ';/?:@&=+$,%#'
_okurlchars = '-.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
              '_abcdefghijklmnopqrstuvwxyz~'

def _normalize_escapes(url):
    """Ensure that escaping in the url is consistent."""
    # url decode any printable normal characters
    # except reserved characters with special meanings in urls
    for c in _urlencpattern.findall(url):
        r = chr(int(c[1:3], 16))
        if r in _okurlchars:
            url = url.replace(c, r)
    # TODO: uppercase any escaped codes left
    # TODO: make this a better performing implementation as this
    #       function costs about 15% of all time during deserialisation 
    # url encode any nonprintable or problematic characters
    # (but not reserved chars)
    url = ''.join(
      [ (x not in _reservedurlchars and
         x not in _okurlchars) and ('%%%02X' % ord(x))
        or x
        for x in url ] )
    return url

def _urlclean(url):
    """Clean the url of uneccesary parts."""
    # make escaping consistent
    url = _normalize_escapes(url)
    # split the url in useful parts
    (scheme, netloc, path, query) = urlparse.urlsplit(url)[:4]
    if ( scheme == 'http' or scheme == 'https' or scheme == 'ftp' ):
        # http(s) urls should have a non-empty path
        if path == '':
            path = '/'
        # make hostname lower case
        (userpass, hostport) = urllib.splituser(netloc)
        netloc = hostport.lower()
        # trim trailing :
        if netloc[-1:] == ':':
            netloc = netloc[:-1]
        if userpass is not None:
            netloc = userpass+'@'+netloc
    # get rid of double slashes in some paths
    if ( scheme == 'file' ):
        path = _doubleslashpattern.sub('/', path)
    # put the url back together again (discarding fragment)
    return urlparse.urlunsplit((scheme, netloc, path, query, ''))

def normalizeurl(url):
    """Return a normalized URL."""
    return _urlclean(url)
