
# problems.py - plugin to list problems
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
# Copyright (C) 2005 Arthur de Jong
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

"""Present an overview of all encountered problems per author."""

__title__ = 'problems by author'
__author__ = 'Arthur de Jong'
__version__ = '1.1'
__description__ = 'This is an overview of all the problems on the site, ' \
                  'grouped by author.'

import plugins
import urllib
import xml.sax.saxutils

def generate(fp,site):
    """Output the overview of problems to the given file descriptor."""
    # make a list of problems per author
    problem_db = {}
    for link in site.linkMap.values():
        # skip external pages
        if not link.isinternal or len(link.pageproblems) == 0:
            continue
        if problem_db.has_key(link.author):
            problem_db[link.author].append(link)
        else:
            problem_db[link.author] = [link]
    # get a list of authors
    authors=problem_db.keys()
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
        # sort pages by url
        problem_db[author].sort(lambda a, b: cmp(a.url, b.url))
        # list problems for this author
        for link in problem_db[author]:
            # present the links
            fp.write(
              '    <li>\n' \
              '     %(link)s\n' \
              '     <ul class="problems">\n' \
              % { 'link':    plugins.make_link(link) })
            # sort problems by name
            link.pageproblems.sort()
            # list the problems
            for problem in link.pageproblems:
                fp.write(
                  '      <li>%(problem)s</li>\n' \
                  % { 'problem':  xml.sax.saxutils.escape(problem) })
            # end the list item
            fp.write(
              '     </ul>\n' \
              '    </li>\n' )
        fp.write(
          '      </ul>\n' \
          '     </li>\n')
    fp.write('   </ul>\n')
