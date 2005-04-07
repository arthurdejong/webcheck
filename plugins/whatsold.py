
# whatsold.py - plugin to list old pages
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

"""Potentially outdated pages"""

__version__ = '1.0'
__author__ = 'mwm@mired.org'

import webcheck
from httpcodes import HTTP_STATUS_CODES
from rptlib import *

Link = webcheck.Link
linkList = Link.linkList
config = webcheck.config

title = "What's Old"

# what's old
def generate():
    print '<div class="table">'
    print '<table border=0 cellpadding=2 cellspacing=2 width="75%">'
    print '\t<tr><th>Link</th><th>Author</th><th>Age</th></tr>'
    urls = linkList.keys()
    urls.sort(sort_by_rev_age)
    for url in urls:
        link=linkList[url]
        if not link.html: continue
        age = link.age
        if age and (age >= config.REPORT_WHATSOLD_URL_AGE):
            print '\t<tr><td>%s</td>' % make_link(url,get_title(url)),
            print '<td>%s</td>' % (link.author),
            print '<td class="time">%s</td></tr>' % age
            add_problem('Old Link: %s days old' % age ,link)
    print '</table>'
    print '</div>'
