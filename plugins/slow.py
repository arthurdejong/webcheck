
# slow.py - plugin that lists pages that could be slow to load
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
# Copyright (C) 2005 Arthur de Jong
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

__title__ = "what's slow"
__author__ = 'Arthur de Jong'

import config
import plugins

def _getsize(link,done=[]):
    """Return the size of the link and all its embedded links, counting each
    link only once."""
    done.append(link)
    if not hasattr(link,"totalSize"):
        size = 0
        if link.size is not None:
            size = link.size
        for l in link.embedded:
            if l not in done:
                size += _getsize(l,done)
        link.totalSize = size
    return link.totalSize

def generate(fp,site):
    """Output the list of large pages to the given file descriptor."""
    # first go over all the links and calculate size if needed
    links = site.linkMap.values()
    reslinks = []
    for link in links:
        if not link.ispage:
            continue
        if not link.isinternal:
            continue
        # calculate size
        size = _getsize(link)
        # TODO: print size nicely
        sizeK = size / 1024
        if sizeK < config.REPORT_SLOW_URL_SIZE:
            continue
        reslinks.append(link)
    # present results
    reslinks.sort(lambda a, b: cmp(a.totalSize, b.totalSize))
    fp.write(
      '   <p class="description">\n'
      '    These pages are probably too big which will be slow to download.\n'
      '   </p>\n'
      '   <ul>\n' )
    for link in reslinks:
        fp.write(
          '    <li>\n'
          '     %(link)s\n'
          '     <ul class="problem">\n'
          '      <li>size: %(size)sK</li>\n'
          '     </ul>\n'
          '    </li>\n'
          % { 'link': plugins.make_link(link),
              'size': sizeK })
        link.add_pageproblem('this page %sK' % str(sizeK)) 
    fp.write(
      '   </ul>\n' )
