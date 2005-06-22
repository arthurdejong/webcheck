
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

import rptlib

def generate(fp,site):
    """Output a sorted list of urls to the specified file descriptor."""
    urls=site.linkMap.keys();
    urls.sort()
    fp.write('<ol>\n')
    for url in urls:
        fp.write('<li>'+rptlib.make_link(url,url)+'</li>')
    fp.write('</ol>\n')
