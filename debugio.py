# Copyright (C) 1998,1999  marduk <marduk@python.net>
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

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.



"""debugio.py: debugging and input/output module
   
   This module contains facilities for printing to standard output.  The use
   of this module is really simple: import it, set DEBUG_LEVEL, and use write()
   whenever you want to print something.  The print function will print to
   standard output depending on DEBUG_LEVEL.
"""
import sys

DEBUG_LEVEL=1

def write(s, level=1, file=sys.stdout):
    """Write s to stdout if DEBUG_LEVEL is >= level"""

    if DEBUG_LEVEL >= level: file.write("%s\n" % s)
