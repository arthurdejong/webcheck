
# anchors.py - plugin check for missing anchors
#
# Copyright (C) 2006 Arthur de Jong
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

def generate(site):
    """Present the list of bad links to the given file descriptor."""
    # find all links with requested anchors
    links = [ x
              for x in site.linkMap.values()
              if len(x.reqanchors)>0 and x.isfetched ]
    # go over list and find missing anchors
    for link in links:
        # check all requested anchors
        for anchor in link.reqanchors:
            # if the anchor is there there is no prolem
            if anchor in link.anchors:
                continue
            # report problem
            for parent in link.reqanchors[anchor]:
                parent.add_pageproblem(
                  'reference to underfined anchor "%(anchor)s"'
                  % { 'anchor': anchor })
