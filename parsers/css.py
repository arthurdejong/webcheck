
# css.py - parser functions for css content
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

"""This modules attempts to parse CSS files.
It currently looks for url() links in stylesheet contents and also
looks for @import processing directives."""

mimetypes = ('text/css',)

import urlparse
import re

# pattern for matching /* ... */ comments in css
_commentpattern = re.compile('/\*.*?\*/', re.IGNORECASE|re.DOTALL)

# pattern for matching @import "url" statments in css
_importpattern = re.compile('@import\s+["\']([^"\']*)["\']',
                            re.IGNORECASE|re.DOTALL)

# pattern for matching url(...) in css
_urlpattern = re.compile('url\(["\']?(.*?)["\']?\)')

def parse(content, link):
    """Parse the specified content and extract information for crawling the
    site further."""
    # strip out comments from the content
    content = _commentpattern.sub('', content)
    # handler @imports
    for i in _importpattern.findall(content):
        link.add_embed(urlparse.urljoin(link.url, i))
    # handle url()s
    for i in _urlpattern.findall(content):
        link.add_embed(urlparse.urljoin(link.url, i))
