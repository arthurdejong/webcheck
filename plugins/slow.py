
# slow.py - plugin that lists pages that could be slow to load
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

"""Present a list of pages that are slow to download."""

__title__ = "what's slow"
__author__ = 'Arthur de Jong'
__version__ = '1.1'

import webcheck
import rptlib

def generate(fp):
    """Output the list of slow pages to the given file descriptor."""
    import time
    fp.write('<div class="table">\n')
    fp.write('<table border="0" cellpadding="2" cellspacing="2" width="75%">\n')
    fp.write('  <tr><th rowspan="2">Link</th>\n')
    fp.write('      <th rowspan="2">Size <br>(Kb)</th>\n')
    fp.write('      <th colspan="3">Time (HH:MM:SS)</th></tr>\n')
    fp.write('  <tr><th>28.8</th><th>ISDN</th><th>T1</th></tr>\n')
    urls = webcheck.Link.linkMap.keys()
    urls.sort(rptlib.sort_by_size)
    for url in urls:
        link = webcheck.Link.linkMap[url]
        if not link.html:
            continue
        sizeK = link.totalSize / 1024
        sizek = link.totalSize * 8 / 1000
        if sizeK < webcheck.config.REPORT_SLOW_URL_SIZE:
            break
        fp.write('  <tr><td>%s</td>' % make_link(url)+'\n')
        fp.write('      <td>%s</td>\n' % sizeK)
        fp.write('      <td class="time">%s</td>\n' \
                 % time.strftime('%H:%M:%S',time.gmtime(int(sizek/28.8))))
        fp.write('      <td class="time">%s</td>\n' \
                 % time.strftime('%H:%M:%S',time.gmtime(int(sizek/56))))
        fp.write('      <td class="time">%s</td></tr>\n' \
                 % time.strftime('%H:%M:%S',time.gmtime(int(sizek/1500))))
        rptlib.add_problem('Slow Link: %sK' % sizeK, link) 
    fp.write('</table>\n')
    fp.write('</div>\n')
