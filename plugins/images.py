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

"""Image Catalog"""

__version__ = '1.0'
__author__ = 'mwm@mired.org'

import webcheck
from httpcodes import HTTP_STATUS_CODES
from rptlib import *

Link = webcheck.Link
linkList = Link.linkList
config = webcheck.config

title = 'Images'

# images
def generate():    
    import math
    imagelist=Link.images.keys()

    currentPic=0
    rows = int(math.ceil(len(imagelist)/config.REPORT_IMAGES_COLS))+1
    print '<div class="table">'
    print '<table border=0 cellspacing="1" cellpadding="0">'
    
    for row in range(rows):
	print'\t<tr>'
	for col in range(config.REPORT_IMAGES_COLS):
	    if currentPic==len(imagelist): break
	    image=imagelist[currentPic]
	    print '\t\t<td>' + \
	      make_link(image,
			'<img src="%s" width="%d" height="%d" alt="%s">' \
		  % (image,config.REPORT_IMAGES_WIDTH,
		     config.REPORT_IMAGES_HEIGHT, image)),
	    print '</td>'
	    currentPic = currentPic + 1

	print '\t</tr>'
    print '</table>'
    print '</div>'
