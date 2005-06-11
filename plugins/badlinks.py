
# badlinks.py - plugin to list bad links
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

"""Present a listing of links that point to non-existant pages."""

__title__ = 'bad links'
__author__ = 'Arthur de Jong'
__version__ = '1.1'

import webcheck
import rptlib

HTTP_STATUS_CODES = {'100':"Continue",
                     '101':"Switching Protocols",
                     '200':"OK",
                     '201':"Created",
                     '202':"Accepted",
                     '204':"No Content",
                     '205':"Reset Content",
                     '206':"Partial Content",
                     '300':"Multiple Choices",
                     '301':"Moved Permanently",
                     '302':"Moved Temporarily",
                     '303':"See Other",
                     '304':"Not Modified",
                     '305':"Use Proxy",
                     '400':"Bad Request",
                     '401':"Unauthorized",
                     '402':"Payment Required",
                     '403':"Forbidden",
                     '404':"Not Found",
                     '405':"Method Not Allowed",
                     '406':"Not Acceptable",
                     '407':"Proxy Authentication Required",
                     '408':"Request Time-out",
                     '409':"Conflict",
                     '410':"Gone",
                     '411':"Length Required",
                     '412':"Precondition Failed",
                     '413':"Request Entity Too Large",
                     '414':"Request-URI Too Large",
                     '415':"Unsupported Media Type",
                     '500':"Internal Server Error",
                     '501':"Not Implemented",
                     '502':"Bad Gateway",
                     '503':"Service Unavailable",
                     '504':"Gateway Time-out",
                     '505':"HTTP Version not supported"
                     }

def generate(fp):
    """Present the list of bad links to the given file descriptor."""
    fp.write('<div class="table">\n')
    fp.write('<table border="0" cellspacing="2" width="75%">\n')
    for url in webcheck.Link.badLinks:
        fp.write('  <tr><td class="blank" colspan="3">&nbsp;</td></tr>\n')
        if webcheck.config.ANCHOR_BAD_LINKS:
            fp.write('  <tr class="link"><th>Link</th>\n')
            fp.write('    <td colspan="2" align="left">'  +rptlib.make_link(url) +'</td></tr>\n')
        else:
            fp.write('  <tr class="link"><th>Link</th>\n')
            fp.write('    <td colspan="2" align="left">%s</td></tr>\n' % url)
        status = str(webcheck.Link.linkMap[url].status)
        if status in HTTP_STATUS_CODES.keys():
            status = status + ": " + HTTP_STATUS_CODES[status]
        fp.write('  <tr class="status"><th>Status</th><td colspan="2">%s</td></tr>\n' % status)
        parents = webcheck.Link.linkMap[url].parents
        fp.write('  <tr class="parent"><th rowspan="%s">Parents</th>\n' % len(parents))
        parents.sort(rptlib.sort_by_author)
        for parent in parents:
            fp.write('    <td>%s</td>\n' % rptlib.make_link(parent))
            fp.write('    <td>%s</td>\n  </tr>\n' % (str(webcheck.Link.linkMap[parent].author)))
            rptlib.add_problem("Bad Link: " + url, webcheck.Link.linkMap[parent])
    fp.write('</table>\n')
    fp.write('</div>\n')
