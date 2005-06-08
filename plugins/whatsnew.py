
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
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

"""Recently modified pages"""

__version__ = '1.0'
__author__ = 'mwm@mired.org'

import webcheck
from httpcodes import HTTP_STATUS_CODES
from rptlib import *

Link = webcheck.Link
linkMap = Link.linkMap
config = webcheck.config

title = "What's New"

# what's new
def generate(fp):
    fp.write('<div class="table">\n')
    fp.write('<table border="0" cellpadding="2" cellspacing="2" width="75%">\n')
    fp.write('  <tr><th>Link</th><th>Author</th><th>Age</th></tr>\n')
    urls = linkMap.keys()
    urls.sort(sort_by_age)
    for url in urls:
        link=linkMap[url]
        if not link.html:
            continue
        age = link.age
        if (age is not None) and (age <= config.REPORT_WHATSNEW_URL_AGE):
            fp.write('  <tr><td>%s</td>\n' % make_link(url,get_title(url)))
            fp.write('      <td>%s</td>\n' % link.author)
            fp.write('      <td class="time">%s</td></tr>\n' % age)
    fp.write('</table>\n')
    fp.write('</div>\n')
