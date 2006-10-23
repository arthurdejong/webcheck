
# sitemap.py - plugin to generate a sitemap
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

"""Present a site map of the checked site."""

__title__ = 'site map'
__author__ = 'Arthur de Jong'
__outputfile__ = 'index.html'

import config
import plugins

def _explore(fp, link, explored=None, depth=0, indent='    '):
    """Recursively do a breadth first traversal of the graph of links on the
    site. Prints the html results to the file descriptor."""
    # set up explored
    if explored is None:
        explored = [ link ]
    # output this link
    fp.write(indent+'<li>\n')
    fp.write(indent+' '+plugins.make_link(link)+'\n')
    # only check children if we are not too deep yet
    if depth <= config.REPORT_SITEMAP_LEVEL:
        # figure out the links to follow and ensure that they are only
        # explored from here
        children = []
        for child in link.pagechildren:
            # skip pages that have the wrong depth, are not internal or have
            # already been visited
            if child.depth != depth+1 or not child.isinternal or child in explored:
                continue
            # set child as explored and add to to explore list
            explored.append(child)
            children.append(child)
        # go over the children and present them as a list
        if len(children) > 0:
            fp.write(indent+' <ul>\n')
            children.sort(lambda a, b: cmp(a.url, b.url))
            for child in children:
                _explore(fp, child, explored, depth+1, indent+'  ')
            fp.write(indent+' </ul>\n')
    fp.write(indent+'</li>\n')

def generate(site):
    """Output the sitemap to the specified file descriptor."""
    fp = plugins.open_html(plugins.sitemap, site)
    # output the site structure using breadth first traversal
    fp.write(
      '   <p class="description">\n'
      '    This an overview of the crawled site.\n'
      '   </p>\n'
      '   <ul>\n' )
    explored = []
    for l in site.bases:
        explored.append(l)
    for l in site.bases:
        _explore(fp, l, explored)
    fp.write(
      '   </ul>\n' )
    plugins.close_html(fp)
