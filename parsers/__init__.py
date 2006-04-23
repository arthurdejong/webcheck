
# __init__.py - general content-type parser interface
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

"""This package groups all the supported content-types.

A content-type module can be requested by the get_parsemodule() function.
Each module should export the following function:

    parse(content, link)
        Based on the content, fill in the common fields of the link object."""

# the modules that should be imported
_modules = ('html', 'css')

# a map of mimetypes to modules
_parsermodules = {}

def _init_modules():
    """Initialize the modules."""
    # go throught all known modules to probe the content-types
    # (do this only once)
    for mod in _modules:
        parser = __import__('parsers.'+mod, globals(), locals(), [mod])
        for mimetype in parser.mimetypes:
            _parsermodules[mimetype] = parser

def get_parsermodule(mimetype):
    """Look up the correct module for the specified mimetype."""
    if _parsermodules == {}:
        _init_modules()
    # check if we have a supported content-type
    if _parsermodules.has_key(mimetype):
        return _parsermodules[mimetype]
    return None

def get_mimetypes():
    """Return a list of supported mime types that can be parsed
    by the installed parsers."""
    if _parsermodules == {}:
        _init_modules()
    return _parsermodules.keys()
