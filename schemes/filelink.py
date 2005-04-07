
# filelink.py handle urls with a file scheme
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk) <marduk@python.net>
# Copyright (C) 2002 Mike Meyer <mwm@mired.org>
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
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

"""This module defines the functions needed for creating Link objects for urls
using the file scheme"""

import urlparse
import os
import time
import mimetypes
import myUrlLib
import re

mimetypes.types_map['.shtml']='text/html'

def init(self, url, parent):
    self.URL = myUrlLib.basejoin(parent,url)
    parsed = urlparse.urlparse(self.URL,'file',0)
    filename = parsed[2]
    if os.name != 'posix':
        filename = re.sub("^/\(//\)?\([a-zA-Z]\)[|:]","\\2:",filename)
    try:
        stats = os.stat(filename)
    except os.error:
        self.set_bad_link(self.URL, "No such file or directory")
        return

    self.size = stats[6]
    
    lastMod = stats[8]
    self.age = int((time.time()-lastMod)/myUrlLib.SECS_PER_DAY)
    
    self.type = mimetypes.guess_type(url)[0]
    if self.type is None: self.type = 'application/octet-stream' # good enough?

def get_document(url):
    parsed = urlparse.urlparse(url,'file',0)
    filename = parsed[2]
    if os.name != 'posix':
        filename = re.sub("^/\(//\)?\([a-zA-Z]\)[|:]","\\2:",filename)
    
    return open(filename,'r').read()
    
