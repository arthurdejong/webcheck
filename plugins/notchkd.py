
# notchkd.py - plugin to list links that were not followed
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk) <marduk@python.net>
# Copyright (C) 2002 Mike Meyer <mwm@mired.org>
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

def generate():
    print '<div class="table">'
    print '<table border=0 cellpadding=2 cellspacing=2 width="75%">'
    for url in Link.notChecked:
        print '  <tr><th colspan=4>%s</th></tr>' % make_link(url,url)
        print '  <tr class="parent"><th rowspan="%s">Parent</th>' % len(linkMap[url].parents)
        for parent in linkMap[url].parents:
            print '    ',
            if parent != linkMap[url].parents[0]: print '<tr>',
            print '<td colspan=2>%s</td>' % make_link(parent,get_title(parent)),
            print '<td>%s</td></tr>' % (linkMap[parent].author)
        print '\n  <tr><td class="blank" colspan=4>&nbsp;</td></tr>\n'
    print '</table>'
    print '</div>'
