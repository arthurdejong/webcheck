
# sitemap.py - plugin to generate a sitemap
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

"""Present a sitemap of the visited site."""

__title__ = 'site map'
__author__ = 'Arthur de Jong'
__version__ = '1.1'

import rptlib
import config

def _explore(fp, site, link, explored={}, level=0):
    """Recursively do a breadth-first traversal of the graph of links
    on the site.  Returns a list of HTML fragments that can be printed
    to produce a site map."""
    explored[link.URL]=True
    # output this link
    fp.write('<li>\n')
    if (link.URL in site.badLinks) and not config.ANCHOR_BAD_LINKS:
        fp.write(link.URL+'\n')
    else:
        fp.write(rptlib.make_link(link.URL)+'\n')
    # only check children if we are not too deep yet
    if level <= config.REPORT_SITEMAP_LEVEL:
        # figure out the links to follow and ensure that they are only
        # explored from here
        to_explore = []
        for i in link.children:
            # skip pages that have already been traversed
            if explored.has_key(i):
                continue
            # mark the link as explored
            explored[i]=True
            to_explore.append(i)
        # go over the children and present them as a list
        if len(to_explore) > 0:
            fp.write('<ul>\n')
            for i in to_explore:
                _explore(fp,site,site.linkMap[i],explored,level+1)
            fp.write('</ul>\n')
    fp.write('</li>\n')

def generate(fp,site):
    """Output the sitemap to the specified file descriptor."""
    fp.write('<ul>\n')
    _explore(fp,site,site.linkMap[site.base])
    fp.write('</ul>\n')
