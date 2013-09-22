
# size.py - plugin that lists pages that could be slow to load
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

"""Present a list of pages that are large and probably slow to download."""

__title__ = "what's big"
__author__ = 'Arthur de Jong'
__outputfile__ = 'size.html'

from webcheck import config
from webcheck.db import Session, Link
from webcheck.output import render


def get_size(link, seen=None):
    """Return the size of the link and all its embedded links, counting each
    link only once."""
    # make a new list
    if seen is None:
        seen = set()
    # add this link to the list
    seen.add(link)
    # if we don't known about our total size yet, calculate
    if not hasattr(link, 'total_size'):
        # add our size
        size = link.size or 0
        # add sizes of embedded objects
        for embed in link.embedded:
            if embed not in seen:
                size += get_size(embed, seen)
        link.total_size = size
    return link.total_size


def generate(crawler):
    """Output the list of large pages."""
    session = Session()
    links = session.query(Link).filter_by(is_page=True, is_internal=True)
    links = [x for x in links
             if get_size(x) >= config.REPORT_SLOW_URL_SIZE * 1024]
    links.sort(lambda a, b: cmp(b.total_size, a.total_size))
    render(__outputfile__, crawler=crawler, title=__title__,
           links=links)
    session.close()
