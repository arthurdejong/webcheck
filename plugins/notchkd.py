
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

"""Generate an overview of pages that were not checked."""

__title__ = 'not checked'
__author__ = 'Arthur de Jong'
__version__ = '1.1'

import rptlib

def generate(fp,site):
    """Output the list of not checked pages to the given file descriptor."""
    fp.write('<div class="table">\n')
    fp.write('<table border="0" cellpadding="2" cellspacing="2" width="75%">\n')
    for url in site.notChecked:
        fp.write('  <tr><th colspan="4">%s</th></tr>\n' % rptlib.make_link(url,url))
        fp.write('  <tr class="parent"><th rowspan="%s">Parent</th>\n' % len(site.linkMap[url].parents))
        for parent in site.linkMap[url].parents:
            fp.write('    ')
            if parent != site.linkMap[url].parents[0]:
                fp.write('<tr>\n')
            fp.write('<td colspan="2">%s</td>\n' % rptlib.make_link(parent))
            fp.write('<td>%s</td></tr>\n' % (site.linkMap[parent].author))
        fp.write('\n  <tr><td class="blank" colspan="4">&nbsp;</td></tr>\n')
    fp.write('</table>\n')
    fp.write('</div>\n')
