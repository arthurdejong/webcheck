
# urllist.py - plugin to generate a list of visited urls
#
# Copyright (C) 2005, 2006 Arthur de Jong
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

"""Present a list of visited urls."""

__title__ = 'url list'
__author__ = 'Arthur de Jong'
__outputfile__ = 'urllist.html'

import plugins

def generate(site):
    """Output a sorted list of urls to the specified file descriptor."""
    fp = plugins.open_html(plugins.urllist, site)
    fp.write(
      '   <p class="description">\n'
      '    This is the list of all urls encountered during the examination of\n'
      '    the website. It lists internal as well as external and\n'
      '    non-examined urls.\n'
      '   </p>\n'
      '   <ol>\n' )
    urls = site.linkMap.keys()
    urls.sort()
    for url in urls:
        fp.write('    <li>'+plugins.make_link(site.linkMap[url], url)+'</li>\n')
    fp.write(
      '   </ol>\n' )
    plugins.close_html(fp)
