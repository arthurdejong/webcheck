
# size.py - plugin that lists pages that could be slow to load
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

"""Present a list of pages that are large and probably slow to download."""

__title__ = "what's big"
__author__ = 'Arthur de Jong'
__outputfile__ = 'size.html'

import config
import plugins

def _getsize(link, done=[]):
    """Return the size of the link and all its embedded links, counting each
    link only once."""
    done.append(link)
    if not hasattr(link, "totalSize"):
        size = 0
        if link.size is not None:
            size = link.size
        for l in link.embedded:
            if l not in done:
                size += _getsize(l,done)
        link.totalSize = size
    return link.totalSize

def generate(site):
    """Output the list of large pages to the given file descriptor."""
    # get all internal pages
    links = filter(lambda a: a.ispage and a.isinternal, site.linkMap.values())
    # calculate size of links
    links = filter(lambda a: _getsize(a) >= config.REPORT_SLOW_URL_SIZE*1024, links)
    # sort links by size
    links.sort(lambda a, b: cmp(a.totalSize, b.totalSize))
    # present results
    fp = plugins.open_html(plugins.size, site)
    if not links:
        fp.write(
          '   <p class="description">\n'
          '    No pages over %(size)sK were found.\n'
          '   </p>\n'
          % { 'size': config.REPORT_SLOW_URL_SIZE })
        plugins.close_html(fp)
        return
    fp.write(
      '   <p class="description">\n'
      '    These pages are probably too big (over %(size)sK) which could be\n'
      '    slow to download.\n'
      '   </p>\n'
      '   <ul>\n'
      % { 'size': config.REPORT_SLOW_URL_SIZE })
    for link in links:
        size = plugins.get_size(link.totalSize)
        fp.write(
          '    <li>\n'
          '     %(link)s\n'
          '     <ul class="problem">\n'
          '      <li>size: %(size)s</li>\n'
          '     </ul>\n'
          '    </li>\n'
          % { 'link': plugins.make_link(link),
              'size': size })
        link.add_pageproblem(
          'this page and its components is %(size)s' 
          % { 'size': size })
    fp.write(
      '   </ul>\n' )
    plugins.close_html(fp)
