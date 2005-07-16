
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
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

"""Present a list of pages that are large and probably slow to download."""

__title__ = "what's slow"
__author__ = 'Arthur de Jong'
__version__ = '1.1'
__description__ = 'These pages are probably too big which will be slow to download.'

import config
import plugins

def generate(fp,site):
    """Output the list of large pages to the given file descriptor."""
    fp.write('   <ul>\n')
    links=site.linkMap.values()
    links.sort(lambda a, b: cmp(a.totalSize, b.totalSize))
    for link in links:
        if not link.html:
            continue
        # TODO: print size nicely
        sizeK = link.totalSize / 1024
        if sizeK < config.REPORT_SLOW_URL_SIZE:
            continue
        fp.write(
          '    <li>\n' \
          '     %(link)s\n' \
          '     <div class="status">size: %(size)sK</div>\n' \
          '    </li>\n' \
          % { 'link': plugins.make_link(link.URL),
              'size': sizeK })
        plugins.add_problem('slow Link: %sK' % str(sizeK), link) 
    fp.write('   </ul>\n')
