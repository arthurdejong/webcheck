
# external.py - plugin to list external links
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
# Copyright (C) 2005, 2006, 2009, 2011, 2013 Arthur de Jong
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
from webcheck.output import render


def generate(crawler):
    """Generate the list of external links."""
    session = Session()
    links = session.query(Link).filter(Link.is_internal != True).order_by(Link.url)
    links = links.options(joinedload(Link.linkproblems))
    render(__outputfile__, crawler=crawler, title=__title__,
           links=links)
    session.close()
