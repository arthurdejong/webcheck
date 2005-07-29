
# images.py - plugin to list images referenced on the site
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
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

"""Present a list of images that are on the site."""

__title__ = 'images'
__author__ = 'Arthur de Jong'
__version__ = '1.1'
__description__ = 'This is the list of all images found linked on the ' \
                  'website.'

import plugins
import re

def generate(fp,site):
    """Output a list of images to the given file descriptor."""
    fp.write('<ol>\n')
    links=site.linkMap.values()
    links.sort(lambda a, b: cmp(a.url, b.url))
    # this finds all links with a reasonable image-like content-type
    matcher=re.compile("^image/.*$")
    for link in links:
        if link.ispage or (link.mimetype is None):
            continue
        if matcher.search(link.mimetype):
            fp.write('  <li>%s</li>\n' % plugins.make_link(link,link.url))
    fp.write('</ol>\n')
