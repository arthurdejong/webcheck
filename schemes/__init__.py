
# __init__.py - general scheme interface
#
# Copyright (C) 2005, 2006 Arthur de Jong
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

"""This package groups all the supported schemes.

A scheme module can be requested by the get_schememodule() function.
Each module should export the following function:

    fetch(link, acceptedtypes)
        Fetch the link. Some basic information about the document is
        provided if possible (size, mimetype, mtime, status in case of
        errors, etc). Also the contents of the link is fetched and
        returned if the content type is mentioned in the acceptedtypes
        list."""

import re

# pattern to match valid scheme names
_schemepattern = re.compile('^[A-Za-z][A-Za-z0-9]*$')

# a map of schemes to modules
_schememodules = {}

def get_schememodule(scheme):
    """Look up the correct module for the specified scheme."""
    # check validity of scheme name
    if not _schemepattern.search(scheme):
        return None
    # find module for scheme name
    if not _schememodules.has_key(scheme):
        try:
            _schememodules[scheme] = \
              __import__('schemes.'+scheme, globals(), locals(), [scheme])
        except ImportError:
            _schememodules[scheme] = None
    return _schememodules[scheme]
