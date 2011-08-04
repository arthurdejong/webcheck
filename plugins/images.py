
# images.py - plugin to list images referenced on the site
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
# Copyright (C) 2005, 2006, 2011 Arthur de Jong
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

"""Present a list of images that are on the site."""

__title__ = 'images'
__author__ = 'Arthur de Jong'
__outputfile__ = 'images.html'

import re
from sqlalchemy.sql.expression import or_

import db
import plugins


def generate(site):
    """Output a list of images to the given file descriptor."""
    # get non-page images that have an image/* mimetype
    links = site.links.filter(or_(db.Link.is_page != True, db.Link.is_page == None))
    links = links.filter(db.Link.mimetype.startswith('image/'))
    links = links.order_by('url')
    # present results
    fp = plugins.open_html(plugins.images, site)
    if not links:
        fp.write(
          '   <p class="description">\n'
          '    No images were linked on the website.\n'
          '   </p>\n'
          '   <ol>\n' )
        plugins.close_html(fp)
        return
    fp.write(
      '   <p class="description">\n'
      '    This is the list of all images found linked on the website.\n'
      '   </p>\n'
      '   <ol>\n' )
    for link in links:
        fp.write('    <li>%s</li>\n' % plugins.make_link(link, link.url))
    fp.write(
      '   </ol>\n' )
    plugins.close_html(fp)
