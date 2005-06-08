
# notchkd.py - plugin to list links that were not followed
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

"""Pages which were not checked"""

__version__ = '1.0'
__author__ = 'mwm@mired.org'

import webcheck
from httpcodes import HTTP_STATUS_CODES
from rptlib import *

Link = webcheck.Link
linkMap = Link.linkMap
config = webcheck.config

title = 'Not Checked'

def generate(fp):
    fp.write('<div class="table">\n')
    fp.write('<table border="0" cellpadding="2" cellspacing="2" width="75%">\n')
    for url in Link.notChecked:
        fp.write('  <tr><th colspan=4>%s</th></tr>\n' % make_link(url,url))
        fp.write('  <tr class="parent"><th rowspan="%s">Parent</th>\n' % len(linkMap[url].parents))
        for parent in linkMap[url].parents:
            fp.write('    ')
            if parent != linkMap[url].parents[0]:
                fp.write('<tr>\n')
            fp.write('<td colspan="2">%s</td>\n' % make_link(parent,get_title(parent)))
            fp.write('<td>%s</td></tr>\n' % (linkMap[parent].author))
        fp.write('\n  <tr><td class="blank" colspan="4">&nbsp;</td></tr>\n')
    fp.write('</table>\n')
    fp.write('</div>\n')
