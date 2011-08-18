
# sitemap.py - plugin to generate a sitemap
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
# Copyright (C) 2005, 2006, 2007, 2011 Arthur de Jong
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
import db
import plugins


def add_pagechildren(link, children, explored):
    """Determine the page children of this link, combining the children of
    embedded items and following redirects."""
    # get all internal children
    qry = link.children.filter(db.Link.is_internal == True)
    if link.depth:
        qry = qry.filter((db.Link.depth > link.depth) | (db.Link.depth == None))
    # follow redirects
    children.update(y
                    for y in (x.follow_link() for x in qry)
                    if y and y.is_page and y.is_internal and y.id not in explored)
    explored.update(x.id for x in children)
    # add embedded element's pagechildren (think frames)
    for embed in link.embedded.filter(db.Link.is_internal == True).filter(db.Link.is_page == True):
        # TODO: put this in a query
        if embed.id not in explored and \
           (embed.depth == None or embed.depth > link.depth):
            add_pagechildren(embed, children, explored)


def _explore(fp, link, explored, depth=0, indent='    '):
    """Recursively do a breadth first traversal of the graph of links on the
    site. Prints the html results to the file descriptor."""
    # output this link
    fp.write(indent + '<li>\n')
    fp.write(indent + ' ' + plugins.make_link(link) + '\n')
    # only check children if we are not too deep yet
    if depth <= config.REPORT_SITEMAP_LEVEL:
        # figure out the links to follow and ensure that they are only
        # explored from here
        children = set()
        add_pagechildren(link, children, explored)
        # remove None which could be there as a result of follow_link()
        children.discard(None)
        if children:
            children = list(children)
            # present children as a list
            fp.write(indent + ' <ul>\n')
            children.sort(lambda a, b: cmp(a.url, b.url))
            for child in children:
                _explore(fp, child, explored, depth + 1, indent + '  ')
            fp.write(indent + ' </ul>\n')
    fp.write(indent + '</li>\n')


def generate(site):
    """Output the sitemap to the specified file descriptor."""
    fp = plugins.open_html(plugins.sitemap, site)
    # output the site structure using breadth first traversal
    fp.write(
      '   <p class="description">\n'
      '    This an overview of the crawled site.\n'
      '   </p>\n'
      '   <ul>\n')
    explored = set(x.id for x in site.bases)
    for l in site.bases:
        _explore(fp, l, explored)
    fp.write(
      '   </ul>\n')
    plugins.close_html(fp)
