
# images.py - plugin to list images referenced on the site
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

"""Present a list of images that are on the site."""

__title__ = 'images'
__author__ = 'Arthur de Jong'
__version__ = '1.1'
__description__ = 'This is the list of all images found linked on the ' \
                  'website.'

import plugins

def generate(fp,site):
    """Output a list of images to the given file descriptor."""
    fp.write('<ol>\n')
    images=site.images.values()
    images.sort(lambda a, b: cmp(a.URL, b.URL))
    for image in images:
        fp.write('  <li>%s</li>\n' % plugins.make_link(image.URL,image.URL))
    fp.write('</ol>\n')
