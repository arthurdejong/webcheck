
# notchkd.py - plugin to list links that were not followed
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
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

"""Present an overview of pages that were not checked."""

__title__ = 'not checked'
__author__ = 'Arthur de Jong'
__outputfile__ = 'notchkd.html'

import plugins

def generate(site):
    """Output the list of not checked pages to the given file descriptor."""
    # get all yanked urls
    links = [ x
              for x in site.linkMap.values()
              if x.isyanked ]
    links.sort(lambda a, b: cmp(a.url, b.url))
    # present results
    fp = plugins.open_html(plugins.notchkd, site)
    if not links:
        fp.write(
          '   <p class="description">\n'
          '    All links have been checked.\n'
          '   </p>\n' )
        plugins.close_html(fp)
        return
    fp.write(
      '   <p class="description">\n'
      '    This is the list of all urls that were encountered but not checked\n'
      '    at all during the examination of the website.\n'
      '   </p>\n'
      '   <ol>\n')
    for link in links:
        fp.write(
          '    <li>\n'
          '     %(link)s\n'
          % { 'link': plugins.make_link(link, link.url) })
        # present a list of parents
        plugins.print_parents(fp, link, '     ')
        fp.write(
          '    </li>\n')
    fp.write(
      '   </ol>\n' )
    plugins.close_html(fp)
