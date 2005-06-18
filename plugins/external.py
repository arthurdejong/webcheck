
# external.py - plugin to list external links
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

"""Present a list of external links present on the site."""

__title__ = 'external links'
__author__ = 'Arthur de Jong'
__version__ = '1.1'

import rptlib

def generate(fp,site):
    """Generate the list of external links to the given file descriptor."""
    urls=site.linkMap.keys();
    urls.sort()
    fp.write('<ol>\n')
    for url in urls:
        link=site.linkMap[url]
        if link.external:
            fp.write('  <li>%s</li>\n' % rptlib.make_link(url))
    fp.write('</ol>\n')
