
# new.py - plugin to list recently modified pages
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
# Copyright (C) 2005 Arthur de Jong
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
#
# The files produced as output from the software do not automatically fall
# under the copyright of the software, unless explicitly stated otherwise.

"""Present a list of recently modified pages."""

__title__ = "what's new"
__author__ = 'Arthur de Jong'
__description__ = 'These pages have been recently modified.'

import config
import plugins
import time

SECS_PER_DAY=60*60*24

def generate(fp,site):
    """Output the list of recently modified pages to the specified file descriptor."""
    fp.write('   <ul>\n')
    links=site.linkMap.values()
    links.sort(lambda a, b: cmp(b.mtime, a.mtime))
    for link in links:
        if not link.ispage:
            continue
        if link.mtime is None:
            continue
        if not link.isinternal:
            continue
        age = (time.time()-link.mtime)/SECS_PER_DAY
        if (age is not None) and (age <= config.REPORT_WHATSNEW_URL_AGE):
            fp.write(
              '    <li>\n' \
              '     %(link)s\n' \
              '     <ul class="problems">\n' \
              '      <li>age: %(age)d days</li>\n' \
              '     </ul>\n' \
              '    </li>\n' \
              % { 'link':  plugins.make_link(link),
                  'age':   age })
    fp.write('   </ul>\n')
