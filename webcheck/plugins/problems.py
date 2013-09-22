
# problems.py - plugin to list problems
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
# Copyright (C) 2005, 2006, 2007, 2011, 2013 Arthur de Jong
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

import collections
import re

from webcheck.db import Session, Link
from webcheck.output import render


def mk_id(name):
    """Convert the name to a string that may be used inside an ID
    attribute."""
    name = name.lower()
    name = re.sub('^[^a-z]*', '', name)
    name = re.sub('[^a-z0-9_:.]+', '-', name)
    return name


def generate(crawler):
    """Output the overview of problems per author."""
    session = Session()
    # make a list of problems per author
    problem_db = collections.defaultdict(list)
    # get internal links with page problems
    links = session.query(Link).filter_by(is_internal=True)
    links = links.filter(Link.pageproblems.any()).order_by(Link.url)
    for link in links:
        author = link.author.strip() if link.author else u'Unknown'
        problem_db[author].append(link)
    # get a sorted list of authors
    authors = problem_db.keys()
    authors.sort()
    authors = [(x, problem_db[x]) for x in authors]
    render(__outputfile__, crawler=crawler, title=__title__,
           authors=authors, mk_id=mk_id)
    session.close()
