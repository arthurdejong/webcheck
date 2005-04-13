
# about.py - plugin to list some information about used plugins
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

"""Plugins used in this report"""

# This is a trivial plugin aid developers of linbot pluggins

__version__ = '1.0'
__author__ = 'mwm@mired.org'

import webcheck
from httpcodes import HTTP_STATUS_CODES
from rptlib import *

Link = webcheck.Link
linkMap = Link.linkMap
config = webcheck.config

title = "About&nbsp;Plugins"

def generate():
    print '<div class="table">'
    print '<table border=0 cellpadding=2 cellspacing=2 width="75%">'
    print '<tr><th>Plugin</th><th>Version</th><th>Author</th></tr>'
    for plugin in config.PLUGINS + ['problems']:
        report = __import__('plugins.%s' % plugin,globals(),locals(),[plugin])
        author = report.__author__
        version = report.__version__
        print '<tr><td class="pluginname">%s</td>' % plugin,
        print '<td class="pluginversion">%s</td>' % version,
        print '<td class="pluginauthor">%s</td></tr>' % author 
    print '</table>'
    print '</div>'
