
# images.py - plugin to list images referenced on the site
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

"""Present a list of images that are on the site."""

__title__ = 'images'
__author__ = 'Arthur de Jong'
__outputfile__ = 'images.html'

from webcheck.db import Session, Link
from webcheck.output import render


def generate(crawler):
    """Generate a list of image URLs that were found."""
    session = Session()
    # get non-page links that have an image/* mimetype
    links = session.query(Link)
    links = links.filter((Link.is_page != True) | (Link.is_page == None))
    links = links.filter(Link.mimetype.startswith('image/'))
    links = links.order_by(Link.url)
    render(__outputfile__, crawler=crawler, title=__title__,
           links=links)
    session.close()
