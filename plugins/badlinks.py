# Copyright (C) 1998,1999  marduk <marduk@python.net>
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

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

"""Listing of bad links"""

__version__ = '1.0'
__author__ = 'mwm@mired.org'

import webcheck
from httpcodes import HTTP_STATUS_CODES
from rptlib import *

Link = webcheck.Link
linkList = Link.linkList
config = webcheck.config

title = 'Bad Links'

def generate():
    print '<div class="table">'
    print '<table border=0 cellspacing=2 width="75%">'
    for link in Link.badLinks:
	print '\t<tr><td class="blank" colspan=3>&nbsp;</td></tr>'
	if config.ANCHOR_BAD_LINKS:
	    print '\t<tr class="link"><th>Link</th>',
	    print '<td colspan=2 align=left>'  +make_link(link,link) +'</td></tr>'
	else:
	    print '\t<tr class="link"><th>Link</th>',
	    print '<td colspan=2 align=left>%s</td></tr>' % link
	status = str(linkList[link].status)
	if status in HTTP_STATUS_CODES.keys():
	    status = status + ": " + HTTP_STATUS_CODES[status]
	print '\t<tr class="status"><th>Status</th><td colspan=2>%s</td></tr>' % status
	print '\t<tr class="parent"><th rowspan="%s">Parents</th>' % len(linkList[link].parents)
	parents = linkList[link].parents
	parents.sort(sort_by_author)
	for parent in parents:
	    print '\t\t<td>%s</td>' % make_link(parent,get_title(parent)),
	    print '<td>%s</td>\n\t</tr>' % (str(linkList[parent].author))
	    add_problem("Bad Link: " + link,linkList[parent])
    print '</table>'
    print '</div>'
