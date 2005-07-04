
# whatsnew.py - plugin to list recently modified pages
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

"""Present a list of recently modified pages."""

__title__ = "what's new"
__author__ = 'Arthur de Jong'
__version__ = '1.1'

import config
import rptlib

def generate(fp,site):
    """Output the list of recently modified pages to the specified file descriptor."""
    fp.write('<div class="table">\n')
    fp.write('<table border="0" cellpadding="2" cellspacing="2" width="75%">\n')
    fp.write('  <tr><th>Link</th><th>Author</th><th>Age</th></tr>\n')
    links=site.linkMap.values()
    links.sort(lambda a, b: cmp(a.age, b.age))
    for link in links:
        if not link.html:
            continue
        age = link.age
        if (age is not None) and (age <= config.REPORT_WHATSNEW_URL_AGE):
            fp.write('  <tr><td>%s</td>\n' % rptlib.make_link(link.URL))
            fp.write('      <td>%s</td>\n' % link.author)
            fp.write('      <td class="time">%s</td></tr>\n' % age)
    fp.write('</table>\n')
    fp.write('</div>\n')
