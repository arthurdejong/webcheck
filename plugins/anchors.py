
# anchors.py - plugin check for missing anchors
#
# Copyright (C) 2006, 2007, 2011 Arthur de Jong
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

"""Find references to undefined anchors.

This plugin does not output any files, it just finds problems."""

__title__ = 'missing anchors'
__author__ = 'Arthur de Jong'

from sqlalchemy.orm.session import object_session

import db


def generate(site):
    """Present the list of bad links to the given file descriptor."""
    # find all fetched links with requested anchors
    links = site.links.filter(db.Link.reqanchors.any()).filter(db.Link.fetched != None)
    # go over list and find missing anchors
    for link in links:
        # check that all requested anchors exist
        for anchor in link.reqanchors:
            # if the anchor is not there there, report problem
            if not link.anchors.filter(db.Anchor.anchor == anchor.anchor).first():
                anchor.parent.add_pageproblem(
                  u'bad link: %(url)s#%(anchor)s: unknown anchor'
                  % {'url': link.url,
                     'anchor': anchor })
    # FIXME: commit changes in session
