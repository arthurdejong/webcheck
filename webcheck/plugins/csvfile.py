
# csvfile.py - plugin to generate a CSV file of visited urls
#
# Copyright (C) 2013 Arthur de Jong
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

"""generate a CSV file of visited urls."""

__title__ = 'CSV file'
__author__ = 'Arthur de Jong'
__outputfile__ = 'urls.csv'

import csv

from webcheck.db import Session, Link
from webcheck.output import open_file

def _conv(value):
    if value is None:
        return ''
    if isinstance(value, int):
        return str(value)
    if isinstance(value, unicode):
        return value.encode('utf-8')
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    return value


def generate(crawler):
    """Output a sorted list of URLs."""
    session = Session()
    links = session.query(Link).order_by(Link.url)
    writer = csv.writer(open_file(__outputfile__, is_text=False))
    writer.writerow((
        'URL', 'Title', 'Depth', 'Internal', 'Fetched', 'Status',
        'Size'))
    # TODO: add number of parents and number of clildren/embedded
    # TODO: add linkproblems and pageproblems
    for link in links:
        row = (
            link.url, link.title, link.depth,
            'internal' if link.is_internal else 'external',
            link.fetched or link.yanked, link.status, link.size)
        writer.writerow([_conv(x) for x in row])
    session.close()
