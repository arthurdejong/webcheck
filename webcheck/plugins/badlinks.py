
# badlinks.py - plugin to list bad links
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

"""Present a listing of links that point to non-existent pages."""

__title__ = 'bad links'
__author__ = 'Arthur de Jong'
__outputfile__ = 'badlinks.html'

from sqlalchemy.orm import joinedload

from webcheck.db import Session, Link
import webcheck.plugins


def postporcess(crawler):
    """Add all bad links as pageproblems on pages where they are linked."""
    session = Session()
    # find all links with link problems
    links = session.query(Link).filter(Link.linkproblems.any()).options(joinedload(Link.linkproblems))
    # TODO: probably make it a nicer query over all linkproblems
    for link in links:
        # add a reference to the problem map
        for problem in link.linkproblems:
            for parent in link.parents:
                parent.add_pageproblem('bad link: %s: %s' % (link.url, problem))
    session.commit()


def generate(crawler):
    """Present the list of bad links."""
    session = Session()
    # find all links with link problems
    links = session.query(Link).filter(Link.linkproblems.any()).order_by(Link.url).options(joinedload(Link.linkproblems))
    # present results
    fp = webcheck.plugins.open_html(webcheck.plugins.badlinks, crawler)
    if not links:
        fp.write(
          '   <p class="description">\n'
          '    There were no problems retrieving links from the website.\n'
          '   </p>\n')
        webcheck.plugins.close_html(fp)
        return
    fp.write(
      '   <p class="description">\n'
      '    These links could not be retrieved during the crawling of the website.\n'
      '   </p>\n'
      '   <ol>\n')
    for link in links:
        # list the link
        fp.write(
          '    <li>\n'
          '     %(badurl)s\n'
          '     <ul class="problems">\n'
          % {'badurl':  webcheck.plugins.make_link(link, link.url)})
        # list the problems
        for problem in link.linkproblems:
            fp.write(
              '      <li>%(problem)s</li>\n'
              % {'problem':  webcheck.plugins.htmlescape(problem)})
        fp.write(
          '     </ul>\n')
        # present a list of parents
        webcheck.plugins.print_parents(fp, link, '     ')
        fp.write(
          '    </li>\n')
    fp.write(
      '   </ol>\n')
    webcheck.plugins.close_html(fp)
