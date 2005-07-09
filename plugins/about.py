
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
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

"""Present an overview of the plugins that are used."""

__title__ = 'about plugins'
__author__ = 'Arthur de Jong'
__version__ = '1.1'
__description__ = 'This is a more detailed view of the used plugins.'

import config
import xml.sax.saxutils

def generate(fp,site):
    """Output a list of modules, it's authors and it's version to the file descriptor."""
    fp.write('   <ul>\n')
    for plugin in config.PLUGINS:
        report = __import__('plugins.'+plugin,globals(),locals(),[plugin])
        fp.write(
          '    <li>\n' \
          '      <strong>%s</strong><br />\n' \
          % xml.sax.saxutils.escape(report.__title__) )
        #if hasattr(report,"__description__"):
        #    fp.write('      %s<br />\n' % xml.sax.saxutils.escape(report.__description__))
        if hasattr(report,"__author__"):
            fp.write('      author: %s<br />\n' % xml.sax.saxutils.escape(report.__author__))
        if hasattr(report,"__version__"):
            fp.write('      version: %s<br />\n' % xml.sax.saxutils.escape(report.__version__))
    fp.write('   </ul>\n')
