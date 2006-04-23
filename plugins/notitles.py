
# notitles.py - plugin to list pages without titles
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

"""List pages without a title."""

__title__ = 'missing titles'
__author__ = 'Arthur de Jong'
__outputfile__ = 'notitles.html'

import plugins

def generate(site):
    """Output the list of pages without a title to the given file descriptor."""
    # get all internal pages without a title
    links = [ x
              for x in site.linkMap.values()
              if x.ispage and
                 x.isinternal and
                 (x.title is None or x.title == '') ]
    links.sort(lambda a, b: cmp(a.url, b.url))
    # present results
    fp = plugins.open_html(plugins.notitles, site)
    if not links:
        fp.write(
          '   <p class="description">\n'
          '    All pages had a title specified.\n'
          '   </p>\n' )
        plugins.close_html(fp)
        return
    fp.write(
      '   <p class="description">\n'
      '    This is the list of all (internal) pages without a proper title\n'
      '    specified.\n'
      '   </p>\n'
      '   <ol>\n')
    for link in links:
        fp.write(
          '    <li>%(link)s</li>\n'
          % { 'link': plugins.make_link(link,link.url) })
        link.add_pageproblem('missing title')
    fp.write(
      '   </ol>\n' )
    plugins.close_html(fp)
