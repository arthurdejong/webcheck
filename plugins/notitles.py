
# notitles.py - plugin to list pages without titles
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

"""List pages without a title."""

__title__ = 'missing titles'
__author__ = 'Arthur de Jong'
__description__ = 'This is the list of all (internal) pages without a ' \
                  'proper title specified.'

import plugins

def generate(fp,site):
    """Output the list of pages without a title to the given file descriptor."""
    fp.write('   <ol>\n')
    links=site.linkMap.values()
    links.sort(lambda a, b: cmp(a.url, b.url))
    for link in links:
        if not link.isinternal:
            continue
        # also check that we're testing html content
        if link.ispage and (link.title is None):
            fp.write(
              '    <li>%(link)s</li>\n' \
              % { 'link': plugins.make_link(link,link.url) })
            link.add_pageproblem("missing title")
    fp.write('   </ol>\n')
