
# problems.py - plugin to list problems
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

"""Present an overview of all encountered problems per author."""

__title__ = 'problems by author'
__author__ = 'Arthur de Jong'
__outputfile__ = 'problems.html'

import urllib

import db
import plugins


def _mk_id(name):
    """Convert the name to a string that may be used inside an
    ID attribute."""
    # convert to lowercase first
    name = name.lower()
    import re
    # strip any leading non alpha characters
    name = re.sub('^[^a-z]*','',name)
    # remove any non-allowed characters
    name = re.sub('[^a-z0-9_:.]+','-',name)
    # we're done
    return name

def generate(site):
    """Output the overview of problems to the given file descriptor."""
    # make a list of problems per author
    problem_db = {}
    # get internal links with page problems
    links = site.links.filter_by(is_internal=True)
    links = links.filter(db.Link.pageproblems.any()).order_by(db.Link.url)
    for link in links:
        # make a normal name for the author
        if link.author:
            author = link.author.strip()
        else:
            author = unicode('Unknown')
        # store the problem
        if problem_db.has_key(author):
            problem_db[author].append(link)
        else:
            problem_db[author] = [link]
    fp = plugins.open_html(plugins.problems, site)
    if not problem_db:
        fp.write(
          '   <p class="description">\n'
          '    No problems were found on this site, hurray.\n'
          '   </p>\n' )
        plugins.close_html(fp)
        return
    # print description
    fp.write(
      '   <p class="description">\n'
      '    This is an overview of all the problems on the site, grouped by\n'
      '    author.\n'
      '   </p>\n' )
    # get a list of authors
    authors = problem_db.keys()
    authors.sort()
    # generate short list of authors
    if len(authors) > 1:
        fp.write('   <ul class="authorlist">\n')
        for author in authors:
            fp.write(
              '    <li><a href="#author_%(authorref)s">Author: %(author)s</a></li>\n'
              % { 'authorref': plugins.htmlescape(_mk_id(author)),
                  'author':    plugins.htmlescape(author) })
        fp.write('   </ul>\n')
    # generate problem report
    fp.write('   <ul>\n')
    for author in authors:
        fp.write(
          '     <li id="author_%(authorref)s">\n'
          '      Author: %(author)s\n'
          '      <ul>\n'
          % { 'authorref': plugins.htmlescape(_mk_id(author)),
              'author':    plugins.htmlescape(author) })
        # sort pages by url
        problem_db[author].sort(lambda a, b: cmp(a.url, b.url))
        # list problems for this author
        for link in problem_db[author]:
            # present the links
            fp.write(
              '    <li>\n'
              '     %(link)s\n'
              '     <ul class="problems">\n'
              % { 'link':    plugins.make_link(link) })
            # sort problems by name
            link.pageproblems.sort()
            # list the problems
            for problem in link.pageproblems:
                fp.write(
                  '      <li>%(problem)s</li>\n'
                  % { 'problem':  plugins.htmlescape(problem) })
            # end the list item
            fp.write(
              '     </ul>\n'
              '    </li>\n' )
        fp.write(
          '      </ul>\n'
          '     </li>\n' )
    fp.write(
      '   </ul>\n' )
    plugins.close_html(fp)
