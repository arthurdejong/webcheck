
# new.py - plugin to list recently modified pages
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
# Copyright (C) 2005, 2006, 2011 Arthur de Jong
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

"""Present a list of recently modified pages."""

__title__ = "what's new"
__author__ = 'Arthur de Jong'
__outputfile__ = 'new.html'

import time

from webcheck import config
from webcheck.db import Session, Link
import webcheck.plugins


SECS_PER_DAY = 60 * 60 * 24


def generate(crawler):
    """Output the list of recently modified pages."""
    session = Session()
    # the time for which links are considered new
    newtime = time.time() - SECS_PER_DAY * config.REPORT_WHATSNEW_URL_AGE
    # get all internal pages that are new
    links = session.query(Link).filter_by(is_page=True, is_internal=True)
    links = links.filter(Link.mtime > newtime).order_by(Link.mtime.desc())
    # present results
    fp = webcheck.plugins.open_html(webcheck.plugins.new, crawler)
    if not links.count():
        fp.write(
          '   <p class="description">\n'
          '    No pages were found that were modified within the last %(new)d days.\n'
          '   </p>\n'
          % {'new': config.REPORT_WHATSNEW_URL_AGE})
        webcheck.plugins.close_html(fp)
        return
    fp.write(
      '   <p class="description">\n'
      '    These pages have been recently modified (within %(new)d days).\n'
      '   </p>\n'
      '   <ul>\n'
      % {'new': config.REPORT_WHATSNEW_URL_AGE})
    for link in links:
        age = (time.time() - link.mtime) / SECS_PER_DAY
        fp.write(
          '    <li>\n'
          '     %(link)s\n'
          '     <ul class="problems">\n'
          '      <li>age: %(age)d days</li>\n'
          '     </ul>\n'
          '    </li>\n'
          % {'link': webcheck.plugins.make_link(link),
             'age':  age})
    fp.write('   </ul>\n')
    webcheck.plugins.close_html(fp)
