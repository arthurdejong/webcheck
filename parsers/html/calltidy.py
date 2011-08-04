
# calltidy.py - parser functions for html content
#
# Copyright (C) 2008, 2011 Arthur de Jong
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

import tidy
import config
import parsers.html

def parse(content, link):
    """Parse the specified content with tidy and add any errors to the
    link."""
    # only call tidy on internal pages
    if link.is_internal:
        t = tidy.parseString(content, **config.TIDY_OPTIONS)
        for err in t.errors:
            # error messages are escaped so we unescape them
            link.add_pageproblem(parsers.html.htmlunescape(unicode(err)))
