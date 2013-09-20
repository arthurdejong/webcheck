#!/usr/bin/env python

# cmd.py - command-line front-end for webcheck
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
# Copyright (C) 2005, 2006, 2007, 2008, 2010, 2011, 2013 Arthur de Jong
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

"""Alternative entry_point for development."""

import os
import sys

from webcheck.cmd import parser, main


if __name__ == '__main__':
    try:
        args = parser.parse_args()
        if args.profile:
            fname = os.path.join(args.output_dir, 'webcheck.prof')
            try:
                import cProfile
            except ImportError:
                import profile as cProfile
            try:
                import sqltap
                sqltap.start()
            except ImportError:
                pass
            cProfile.run('main(vars(args))', fname)
            if 'sqltap' in locals():
                statistics = sqltap.collect()
                sqltap.report(statistics, os.path.join(args.output_dir, 'sqltap.html'))
        else:
            main(vars(args))
    except KeyboardInterrupt:
        sys.stderr.write('Interrupted\n')
        sys.exit(1)
