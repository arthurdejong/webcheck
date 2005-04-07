# Copyright (C) 1998,1999  marduk <marduk@python.net>
# Copyright (C) 2002 Mike Meyer <mwm@mired.org>
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

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

"""Your site at-a-glance"""

__version__ = '1.0'
__author__ = 'mwm@mired.org'

import webcheck
from rptlib import *

title = 'Site Map'
level = 0

def explore(link, explored):
    """Recursively do a breadth-first traversal of the graph of links
    on the site.  Returns a list of HTML fragments that can be printed 
    to produce a site map."""

    global level
    if level > webcheck.config.REPORT_SITEMAP_LEVEL: return []
    # XXX I assume an object without a .URL is something
    # uninteresting? --amk
    if not hasattr(link, 'URL'): return []

    level=level+1
    explored[ link.URL ] = 1
    to_explore = []
    L = ['<ul>']

    # We need to do a breadth-first traversal.  This requires two
    # steps for any given page.  First, we need to make a list of
    # links to be traversed; links that have already been explored can 
    # be ignored.
    
    for i in link.children:
        # Skip pages that have already been traversed
        if explored.has_key( i ): continue
        if (i in webcheck.Link.badLinks) and not webcheck.config.ANCHOR_BAD_LINKS:
            L.append('<li>%s' % i)
        else:
            to_explore.append(i)
        explored[ i ] = 1               # Mark the link as explored

    # Now we loop over the list of links; the traversal will not go to 
    # any pages that are marked as having already been traversed.
    for i in to_explore:
            child = webcheck.Link.linkList[i]
            L.append('<li>%s' % (make_link(i,get_title(i))))
            L = L + explore(child, explored)
            
    L.append( '</ul>' )
    level=level-1

    # If no sub-pages were traversed at all, just return an empty list 
    # to avoid redundant <UL>...</UL> pairs
    if len(L) == 2: return []

    return L
    
# site map
def generate():        
    print make_link(webcheck.Link.base,'Starting Page')
    L = explore(webcheck.Link.base, {})
    for i in L: print i
