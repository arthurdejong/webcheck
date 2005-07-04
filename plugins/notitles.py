
# notitles.py - plugin to list pages without titles
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

"""List pages without a title."""

__title__ = 'missing titles'
__author__ = 'Arthur de Jong'
__version__ = '1.1'

import rptlib

def generate(fp,site):
    """Output the list of pages without a title to the given file descriptor."""
    fp.write('<div class="table">\n')
    fp.write('<table border="0" cellpadding="2" cellspacing="2" width="75%">\n')
    fp.write('  <tr><th>URL</th><th>Author</th></tr>\n')
    links=site.linkMap.values()
    links.sort(lambda a, b: cmp(a.URL, b.URL))
    for link in links:
        if link.external:
            continue
        if link.html and (link.title is None):
            fp.write('  <tr><td>%s</td><td>%s</td></tr>\n' \
                     % (rptlib.make_link(link.URL,link.URL), link.author))
            rptlib.add_problem("No Title",link)
    fp.write('</table>\n')
    fp.write('</div>\n')
