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

"""Pages with no titles"""

__version__ = '1.0'
__author__ = 'mwm@mired.org'

import webcheck
from httpcodes import HTTP_STATUS_CODES
from rptlib import *

Link = webcheck.Link
linkList = Link.linkList
config = webcheck.config

title = 'No Titles'

def generate():
    print '<div class="table">'
    print '<table border=0 cellpadding=2 cellspacing=2 width="75%">'
    print '\t<tr><th>URL</th><th>Author</th></tr>'
    urls = linkList.keys()
    urls.sort(sort_by_author)
    for url in urls:
        link = linkList[url]
        if link.external: continue
        if link.html and (link.title is None):
            print '\t<tr><td>%s</td><td>%s</td></tr>' \
        	  % (make_link(url,url), link.author)
            add_problem("No Title",link)
    print '</table>'
    print '</div>'
