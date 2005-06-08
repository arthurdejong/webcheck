
# badlinks.py - plugin to list bad links
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

"""Listing of bad links"""

__version__ = '1.0'
__author__ = 'mwm@mired.org'

import webcheck
from httpcodes import HTTP_STATUS_CODES
from rptlib import *

linkMap = Link.linkMap

title = 'Bad Links'

def generate(fp):
    fp.write('<div class="table">\n')
    fp.write('<table border="0" cellspacing="2" width="75%">\n')
    for link in webcheck.Link.badLinks:
        fp.write('  <tr><td class="blank" colspan="3">&nbsp;</td></tr>\n')
        if webcheck.config.ANCHOR_BAD_LINKS:
            fp.write('  <tr class="link"><th>Link</th>\n')
            fp.write('    <td colspan="2" align="left">'  +make_link(link,link) +'</td></tr>\n')
        else:
            fp.write('  <tr class="link"><th>Link</th>\n')
            fp.write('    <td colspan="2" align="left">%s</td></tr>\n' % link)
        status = str(linkMap[link].status)
        if status in HTTP_STATUS_CODES.keys():
            status = status + ": " + HTTP_STATUS_CODES[status]
        fp.write('  <tr class="status"><th>Status</th><td colspan="2">%s</td></tr>\n' % status)
        fp.write('  <tr class="parent"><th rowspan="%s">Parents</th>\n' % len(linkMap[link].parents))
        parents = linkMap[link].parents
        parents.sort(sort_by_author)
        for parent in parents:
            fp.write('    <td>%s</td>\n' % make_link(parent,get_title(parent)))
            fp.write('    <td>%s</td>\n  </tr>\n' % (str(linkMap[parent].author)))
            add_problem("Bad Link: " + link,linkMap[parent])
    fp.write('</table>\n')
    fp.write('</div>\n')
