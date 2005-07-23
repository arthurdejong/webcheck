
# sitemap.py - plugin to generate a sitemap
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk) <marduk@python.net>
# Copyright (C) 2002 Mike W. Meyer <mwm@mired.org>
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

"""Present a sitemap of the checked site."""

__title__ = 'site map'
__author__ = 'Arthur de Jong'
__version__ = '1.1'
__description__ = 'This an overview of the crawled site.'

import config
import plugins

def _explore(fp, site, link, explored=None, level=0, indent='    '):
    """Recursively do a breadth-first traversal of the graph of links
    on the site.  Returns a list of HTML fragments that can be printed
    to produce a site map."""
    if explored is None:
        explored = [ link ]
    # output this link
    fp.write(indent+'<li>\n')
    fp.write(indent+' '+plugins.make_link(link.url)+'\n')
    # only check children if we are not too deep yet
    if level <= config.REPORT_SITEMAP_LEVEL:
        # figure out the links to follow and ensure that they are only
        # explored from here
        to_explore = []
        for child in link.children:
            child = child.follow_link()
            # skip pages that have already been traversed
            if child in explored:
                continue
            # skip external links
            if not child.isinternal:
                continue
            # FIXME: find a solution for redirects
            # skip non-page links
            if not child.ispage:
                continue
            # mark the link as explored
            explored.append(child)
            to_explore.append(child)
        # go over the children and present them as a list
        if len(to_explore) > 0:
            fp.write(indent+' <ul>\n')
            to_explore.sort(lambda a, b: cmp(a.url, b.url))
            for i in to_explore:
                _explore(fp,site,i,explored,level+1,indent+'  ')
            fp.write(indent+' </ul>\n')
    fp.write(indent+'</li>\n')

def generate(fp,site):
    """Output the sitemap to the specified file descriptor."""
    fp.write('   <ul>\n')
    _explore(fp,site,site.linkMap[site.base])
    fp.write('   </ul>\n')
