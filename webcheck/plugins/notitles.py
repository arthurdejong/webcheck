
# notitles.py - plugin to list pages without titles
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
# Copyright (C) 2005, 2006, 2011, 2013 Arthur de Jong
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

"""List pages without a title."""

__title__ = 'missing titles'
__author__ = 'Arthur de Jong'
__outputfile__ = 'notitles.html'

from sqlalchemy.sql.functions import char_length

from webcheck.db import Session, Link
import webcheck.plugins


def postprocess(crawler):
    """Add page problems for all pages without a title."""
    session = Session()
    # get all internal pages without a title
    links = session.query(Link).filter_by(is_page=True, is_internal=True)
    links = links.filter((char_length(Link.title) == 0) |
                         (Link.title == None))
    for link in links:
        link.add_pageproblem('missing title')
    session.commit()
    session.close()


def generate(crawler):
    """Output the list of pages without a title."""
    session = Session()
    # get all internal pages without a title
    links = session.query(Link).filter_by(is_page=True, is_internal=True)
    links = links.filter((char_length(Link.title) == 0) |
                         (Link.title == None)).order_by(Link.url)
    # present results
    fp = webcheck.plugins.open_html(webcheck.plugins.notitles, crawler)
    if not links.count():
        fp.write(
          '   <p class="description">\n'
          '    All pages had a title specified.\n'
          '   </p>\n')
        webcheck.plugins.close_html(fp)
        return
    fp.write(
      '   <p class="description">\n'
      '    This is the list of all (internal) pages without a proper title\n'
      '    specified.\n'
      '   </p>\n'
      '   <ol>\n')
    for link in links:
        fp.write(
          '    <li>%(link)s</li>\n'
          % {'link': webcheck.plugins.make_link(link, link.url)})
    fp.write(
      '   </ol>\n')
    webcheck.plugins.close_html(fp)
    session.close()
