
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
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

"""Present an overview of all encoutered problems per author."""

__title__ = 'problems by author'
__author__ = 'Arthur de Jong'
__version__ = '1.1'

import rptlib

def generate(fp,site):
    """Output the overview of problems to the given file descriptor."""
    authors=rptlib.problem_db.keys()
    authors.sort()
    # generate short list of authors
    if len(authors) > 1:
        fp.write('<p class="authorlist">\n')
        for author in authors[:-1]:
            fp.write('<a href="#%s">%s</a>\n' % (author, author))
            fp.write(' | \n')
        fp.write('<a href="#%s">%s</a>\n' % (authors[-1], authors[-1]))
        fp.write('</p>\n')
    # generate problem report
    fp.write('<div class="table">\n')
    fp.write('<table border="0" cellpadding="2" cellspacing="2" width="75%">\n')
    for author in authors:
        fp.write('<tr><th><a name="%s">%s</a></th></tr>\n' % (author,author))
        for type,link in rptlib.problem_db[author]:
            fp.write('<tr><td>%s<br>%s</td></tr>\n' % (rptlib.make_link(link.URL), type))
        fp.write('<tr><td class="blank">&nbsp;</td></tr>\n')
    fp.write('</table>\n')
    fp.write('</div>\n')
