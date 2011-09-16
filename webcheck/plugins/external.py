
# external.py - plugin to list external links
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
# Copyright (C) 2005, 2006, 2009, 2011 Arthur de Jong
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

"""Present a list of external links present on the site."""

__title__ = 'external links'
__author__ = 'Arthur de Jong'
__outputfile__ = 'external.html'

from sqlalchemy.orm import joinedload

from webcheck.db import Session, Link
import webcheck.plugins


def generate(site):
    """Generate the list of external links."""
    session = Session()
    # get all external links
    links = session.query(Link).filter(Link.is_internal != True).order_by(Link.url)
    # present results
    fp = webcheck.plugins.open_html(webcheck.plugins.external, site)
    if not links:
        fp.write(
          '   <p class="description">'
          '    No external links were found on the website.'
          '   </p>\n')
        webcheck.plugins.close_html(fp)
        return
    fp.write(
      '   <p class="description">'
      '    This is the list of all external urls encountered during the'
      '    examination of the website.'
      '   </p>\n'
      '   <ol>\n')
    for link in links.options(joinedload(Link.linkproblems)):
        fp.write(
          '    <li>\n'
          '     %(link)s\n'
          % {'link': webcheck.plugins.make_link(link)})
        # present a list of parents
        webcheck.plugins.print_parents(fp, link, '     ')
        fp.write(
          '    </li>\n')
    fp.write(
      '   </ol>\n')
    webcheck.plugins.close_html(fp)
