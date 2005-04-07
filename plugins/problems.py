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

"""Breakdown of links with problems"""

__version__ = '1.0'
__author__ = 'mwm@mired.org'

import webcheck
from httpcodes import HTTP_STATUS_CODES
from rptlib import *

Link = webcheck.Link
linkList = Link.linkList
config = webcheck.config

title = 'Problems (By&nbsp;Author)'

def generate():
    authors=problem_db.keys()
    authors.sort()
    if len(authors) > 1:
        print '<p class="authorlist">'
        for author in authors[:-1]:
            print '<a href="#%s">%s</a>' % (author, author),
            print " | "
        print '<a href="#%s">%s</a>' % (authors[-1], authors[-1]),
        print '</p>'
    print '<div class="table">'
    print '<table border=0 cellpadding=2 cellspacing=2 width="75%">'
    for author in authors:
        print '<tr><th><a name="%s">%s</a></th></tr>' % (author,author)
        for type,link in problem_db[author]:
            url=`link`
            title=get_title(url)
            print '<tr><td>%s <br>%s</td></tr>' % (make_link(url,title), type)
        print '<tr><td class="blank">&nbsp;</td></tr>\n'
    print '</table>'
    print '</div>'
