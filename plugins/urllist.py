
# urllist.py - plugin to generate a list of visited urls
#
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

"""Present a list of visited urls."""

__title__ = 'url list'
__author__ = 'Arthur de Jong'
__version__ = '1.0'
__description__ = 'This is the list of all urls encountered during the ' \
                  'examination of the website. It lists internal as well ' \
                  'as external and non-examined urls.'

import rptlib

def generate(fp,site):
    """Output a sorted list of urls to the specified file descriptor."""
    fp.write('   <ol>\n')
    links=site.linkMap.values()
    links.sort(lambda a, b: cmp(a.URL, b.URL))
    for link in links:
        fp.write('    <li>'+rptlib.make_link(link.URL,link.URL)+'</li>\n')
    fp.write('   </ol>\n')
