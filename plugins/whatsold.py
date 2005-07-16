
# whatsold.py - plugin to list old pages
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

"""Present a list of potentially outdated pages."""

__title__ = "what's old"
__author__ = 'Arthur de Jong'
__version__ = '1.1'
__description__ = 'These pages habe been modified a long time ago and may be outdated.'

import config
import plugins
import time

SECS_PER_DAY=60*60*24

def generate(fp,site):
    """Output the list of outdated pages to the specified file descriptor."""
    fp.write('   <ul>\n')
    links=site.linkMap.values()
    links.sort(lambda a, b: cmp(a.mtime, b.mtime))
    for link in links:
        if not link.html:
            continue
        if link.mtime is None:
            continue
        age = (time.time()-link.mtime)/SECS_PER_DAY
        if age and (age >= config.REPORT_WHATSOLD_URL_AGE):
            fp.write(
              '    <li>\n' \
              '     %(link)s\n' \
              '     <div class="status">age: %(age)d days</div>\n' \
              '    </li>\n' \
              % { 'link':  plugins.make_link(link.URL),
                  'age':   age })
            # add link to problem database
            plugins.add_problem('Old Link: %s days old' % age ,link)
    fp.write('   </ul>\n')
