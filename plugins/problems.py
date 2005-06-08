
# problems.py - plugin to list problems
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

"""Breakdown of links with problems"""

__version__ = '1.0'
__author__ = 'mwm@mired.org'

import webcheck
from httpcodes import HTTP_STATUS_CODES
from rptlib import *

Link = webcheck.Link
linkMap = Link.linkMap
config = webcheck.config

title = 'Problems (By&nbsp;Author)'

def generate(fp):
    authors=problem_db.keys()
    authors.sort()
    if len(authors) > 1:
        fp.write('<p class="authorlist">\n')
        for author in authors[:-1]:
            fp.write('<a href="#%s">%s</a>\n' % (author, author))
            fp.write(' | \n')
        fp.write('<a href="#%s">%s</a>\n' % (authors[-1], authors[-1]))
        fp.write('</p>\n')
    fp.write('<div class="table">\n')
    fp.write('<table border="0" cellpadding="2" cellspacing="2" width="75%">\n')
    for author in authors:
        fp.write('<tr><th><a name="%s">%s</a></th></tr>\n' % (author,author))
        for type,link in problem_db[author]:
            url=`link`
            title=get_title(url)
            fp.write('<tr><td>%s<br>%s</td></tr>\n' % (make_link(url,title), type))
        fp.write('<tr><td class="blank">&nbsp;</td></tr>\n')
    fp.write('</table>\n')
    fp.write('</div>\n')
