
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

from webcheck import config
from webcheck.db import Session, Link
from webcheck.output import render


def get_children(link, explored):
    """Determine the page children of this link, combining the children of
    embedded items and following redirects."""
    # get all internal children
    qry = link.children.filter(Link.is_internal == True)
    if link.depth:
        qry = qry.filter((Link.depth > link.depth) | (Link.depth == None))
    # follow redirects and return all direct children
    for child in (x.follow_link() for x in qry):
        if child and child.is_page and child.is_internal and child.id not in explored:
            explored.add(child.id)
            yield child
    # add embedded element's pagechildren (think frames)
    for embed in link.embedded.filter(Link.is_internal == True).filter(Link.is_page == True):
        if embed.id not in explored and \
           (embed.depth == None or embed.depth > link.depth):
            for child in get_children(embed, explored):
                yield child


def explore(links, explored=None, depth=0):
    """Recursively do a breadth first traversal of the graph of links on the
    site."""
    if explored is None:
        explored = set(x.id for x in links)
    for link in links:
        children = []
        if depth <= config.REPORT_SITEMAP_LEVEL:
            children = list(get_children(link, explored))
            children.sort(lambda a, b: cmp(a.url, b.url))
        if children:
            yield link, explore(children, explored, depth + 1)
        else:
            yield link, None


def generate(crawler):
    """Output the sitemap."""
    session = Session()
    links = [session.query(Link).filter_by(url=url).first()
             for url in crawler.base_urls]
    links = explore(links)
    render(__outputfile__, crawler=crawler, title=__title__,
           links=links)
