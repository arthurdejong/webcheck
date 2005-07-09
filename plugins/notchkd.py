
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
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

"""Present an overview of pages that were not checked."""

__title__ = 'not checked'
__author__ = 'Arthur de Jong'
__version__ = '1.1'
__description__ = 'This is the list of all urls that were encountered but ' \
                  'not checked at all during the examination of the website.'

import rptlib

def generate(fp,site):
    """Output the list of not checked pages to the given file descriptor."""
    fp.write('   <ol>\n')
    site.notChecked.sort()
    site.notChecked.sort()
    for url in site.notChecked:
        fp.write(
          '    <li>\n' \
          '     %(link)s\n' \
          % { 'link': rptlib.make_link(url,url) })
        # present a list of parents
        rptlib.print_parents(fp,site.linkMap[url],'     ')
        fp.write(
          '    </li>\n')
    fp.write('   </ol>\n')
