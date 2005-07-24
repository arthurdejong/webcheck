
# badlinks.py - plugin to list bad links
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk) <marduk@python.net>
# Copyright (C) 2002 Mike W. Meyer <mwm@mired.org>
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

"""Present a listing of links that point to non-existant pages."""

__title__ = 'bad links'
__author__ = 'Arthur de Jong'
__version__ = '1.1'
__description__ = 'These links had problems with retreival during the ' \
                  'crawling of the website.'

import config
import plugins
import xml.sax.saxutils

def generate(fp,site):
    """Present the list of bad links to the given file descriptor."""
    fp.write('   <ol>\n')
    links=site.linkMap.values()
    links.sort(lambda a, b: cmp(a.url, b.url))
    for link in links:
        if link.status is None:
            continue
        status = str(link.status)
        fp.write(
          '    <li>\n' \
          '     %(badurl)s\n' \
          '     <div class="status">%(status)s</div>\n' \
          % { 'badurl':  plugins.make_link(link.url,link.url),
              'status':  xml.sax.saxutils.escape(status) })
        # present a list of parents
        link.parents.sort()
        plugins.print_parents(fp,link,'     ')
        # add a reference to the problem map
        for parent in link.parents:
            plugins.add_problem("Bad Link: " + link.url, parent)
        fp.write('    </li>\n')
    fp.write('   </ol>\n')
