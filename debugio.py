
# debugio.py - output logging module
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
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

"""Debugging and message output module.

This module contains facilities for logging program output.  The use of
this module is really simple: import it, set loglevel, and use debug(),
info(), warn() and error() whenever you want to print something."""

import sys

# log levels that can be used
ERROR = 0
WARN  = 1
INFO  = 2
DEBUG = 3

# initialize logging at default level
loglevel = INFO

def debug(msg):
    """Log the message to stderr if loglevel will allow it."""
    if loglevel >= DEBUG:
        sys.stderr.write('webcheck: DEBUG: '+str(msg)+'\n')

def info(msg):
    """Log the message to stdout if loglevel will allow it."""
    if loglevel >= INFO:
        sys.stdout.write('webcheck: '+str(msg)+'\n')
        sys.stdout.flush()

def warn(msg):
    """Log a warning to stderr if loglevel will allow it."""
    if loglevel >= WARN:
        sys.stderr.write('webcheck: Warning: '+str(msg)+'\n')

def error(msg):
    """Log an error to stderr if loglevel will allow it."""
    if loglevel >= ERROR:
        sys.stderr.write('webcheck: Error: '+str(msg)+'\n')
