
# about.py - plugin to list some information about used plugins
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

"""Present an overview of the plugins that are used."""

__title__ = 'about webcheck'
__author__ = 'Arthur de Jong'
__outputfile__ = 'about.html'

from webcheck.db import Session, Link
from webcheck.output import render


def generate(crawler):
    """Output a list of modules, it's authors and the webcheck version."""
    session = Session()
    render(__outputfile__, crawler=crawler, title=__title__,
           numlinks=session.query(Link).count())
    session.close()
