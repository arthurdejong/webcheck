
# file.py - handle urls with a file scheme
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
# Copyright (C) 2005 Arthur de Jong
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

"""This module defines the functions needed for creating Link objects for urls
using the file scheme."""

import urlparse
import urllib
import os
import time
import mimetypes
import re

def get_info(link):
    """Retreive some basic information about the file.
    Store the results in the link object."""
    (scheme, netloc, path, query, fragment) = urlparse.urlsplit(link.url)
    path=urllib.url2pathname(path)
    try:
        stats = os.stat(path)
    except os.error, e:
        link.add_problem(str(e))
        return
    link.size = stats[6]
    link.mtime = stats[8]
    # guess mimetype, falling back to application/octet-stream
    link.type = mimetypes.guess_type(link.url)[0]
    if link.type is None:
        link.type = 'application/octet-stream'

def get_document(link):
    """Return the contents of the document pointed to by the link."""
    (scheme, netloc, path, query, fragment) = urlparse.urlsplit(link.url)
    path=urllib.url2pathname(path)
    return open(path,'r').read()

def fetch(link, mimetypes):
    get_info(link)
    return get_document(link)
