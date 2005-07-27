
# __init__.py - general content-type parser interface
#
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
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

"""This package groups all the supported content-types.

A content-type module can be requested by the get_parsemodule() function.
Each module should export the following function:

    parse(content,link)
        Based on the content fill in the common fields of the link object."""

# a map of schemes to modules
_parsermodules = {}

def get_parsermodule(mimetype):
    """Look up the correct module for the specified mimetype."""
    # go throught all known modules to probe the content-types (do this only once)
    if _parsermodules == {}:
        for m in ('html', 'css'):
            p = __import__('parsers.'+m,globals(),locals(),[m])
            for t in p.mimetypes:
                _parsermodules[t] = p
    # check if we have a supported content-type
    if _parsermodules.has_key(mimetype):
        return _parsermodules[mimetype]
    return None