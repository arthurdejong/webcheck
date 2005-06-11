
# about.py - plugin to list some information about used plugins
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk) <marduk@python.net>
# Copyright (C) 2002 Mike Meyer <mwm@mired.org>
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
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

"""Plugins used in this report"""

__version__ = '1.0'
__author__ = 'mwm@mired.org'
title = "About&nbsp;Plugins"

import webcheck
import rptlib

def generate(fp):
    fp.write('<div class="table">\n')
    fp.write('<table border="0" cellpadding="2" cellspacing="2" width="75%">\n')
    fp.write('<tr><th>Plugin</th><th>Version</th><th>Author</th></tr>\n')
    for plugin in webcheck.config.PLUGINS + ['problems']:
        report = __import__('plugins.'+plugin,globals(),locals(),[plugin])
        fp.write('<tr><td class="pluginname">%s</td>\n' % plugin)
        fp.write('    <td class="pluginversion">%s</td>\n' % report.__version__)
        fp.write('    <td class="pluginauthor">%s</td></tr>\n' % report.__author__)
    fp.write('</table>\n')
    fp.write('</div>\n')
