
# problems.py - plugin to list problems
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
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

"""Present an overview of all encoutered problems per author."""

__title__ = 'problems by author'
__author__ = 'Arthur de Jong'
__version__ = '1.1'
__description__ = 'This is an overview of all the problems on the site, ' \
                  'grouped by author.'

import rptlib
import urllib
import xml.sax.saxutils

def generate(fp,site):
    """Output the overview of problems to the given file descriptor."""
    authors=rptlib.problem_db.keys()
    authors.sort()
    # generate short list of authors
    if len(authors) > 1:
        fp.write('   <ul class="authorlist">\n')
        for author in authors:
            fp.write(
              '    <li><a href="#%(authorref)s">Author: %(author)s</a></li>\n' \
              % { 'authorref': urllib.quote(str(author),''),
                  'author':    xml.sax.saxutils.escape(str(author)) })
        fp.write('   </ul>\n')
    # generate problem report
    fp.write('   <ul>\n')
    for author in authors:
        fp.write(
          '     <li>\n' \
          '      <a name="%(authorref)s">Author: %(author)s</a>\n'
          '      <ul>\n' \
          % { 'authorref': urllib.quote(str(author),''),
              'author':    xml.sax.saxutils.escape(str(author)) })
        # list problems for this author
        for problem,link in rptlib.problem_db[author]:
            fp.write(
              '    <li>\n' \
              '     %(link)s\n' \
              '     <div class="status">%(problem)s</div>\n' \
              '    </li>\n' \
              % { 'link':    rptlib.make_link(link.URL),
                  'problem': xml.sax.saxutils.escape(problem) })
        fp.write(
          '      </ul>\n' \
          '     </li>\n')
    fp.write('   </ul>\n')
