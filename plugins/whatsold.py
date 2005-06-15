
# whatsold.py - plugin to list old pages
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
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

"""Present a list of potentially outdated pages."""

__title__ = "what's old"
__author__ = 'Arthur de Jong'
__version__ = '1.1'

import rptlib
import config

def generate(fp,site):
    """Output the list of outdated pages to the specified file descriptor."""
    fp.write('<div class="table">')
    fp.write('<table border="0" cellpadding="2" cellspacing="2" width="75%">\n')
    fp.write('  <tr><th>Link</th><th>Author</th><th>Age</th></tr>\n')
    urls = site.linkMap.keys()
    urls.sort(rptlib.sort_by_rev_age)
    for url in urls:
        link=site.linkMap[url]
        if not link.html:
            continue
        age = link.age
        if age and (age >= config.REPORT_WHATSOLD_URL_AGE):
            fp.write('  <tr><td>%s</td>\n' % rptlib.make_link(url))
            fp.write('      <td>%s</td>\n' % (link.author))
            fp.write('      <td class="time">%s</td></tr>' % age)
            rptlib.add_problem('Old Link: %s days old' % age ,link)
    fp.write('</table>\n')
    fp.write('</div>\n')
