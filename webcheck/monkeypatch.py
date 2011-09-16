
# monkeypatch.py - add missing functionality to standard modules
#
# Copyright (C) 2011 Arthur de Jong
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

import re
import sys
import urllib
import urlparse


__all__ = []


# This monkeypatches RuleLine.applies_to to support * and $ characters in
# robots.txt path names.
def my_applies_to(ruleline, filename):
    if not hasattr(ruleline, 'pattern'):
        pat = []
        # we need to unescape the * from the path here
        for x in ruleline.path.replace('%2A', '*'):
            if x == '*':
                pat.append('.*')
            elif x == '$':
                pat.append(r'\Z')
            else:
                pat.append(re.escape(x))
        ruleline.pattern = re.compile(''.join(pat) + '(?ms)')
    return bool(ruleline.pattern.match(filename))

from robotparser import RuleLine
RuleLine.applies_to = my_applies_to


# This monkeypatches RobotFileParser.can_fetch to include the query string
# into the tested part of the URL, taken from http://bugs.python.org/issue6325
# this should be fixed in Python 2.7
if sys.version_info < (2, 7):

    def my_can_fetch(rfp, useragent, url):
        """using the parsed robots.txt decide if useragent can fetch url"""
        if rfp.disallow_all:
            return False
        if rfp.allow_all:
            return True
        # search for given user agent matches
        # the first match counts
        parsed_url = urlparse.urlparse(urllib.unquote(url))
        url = urlparse.urlunparse(('', '', parsed_url.path,
        parsed_url.params, parsed_url.query, parsed_url.fragment))
        url = urllib.quote(url)
        if not url:
            url = "/"
        for entry in rfp.entries:
            if entry.applies_to(useragent):
                return entry.allowance(url)
        # try the default entry last
        if rfp.default_entry:
            return rfp.default_entry.allowance(url)
        # agent not found ==> access granted
        return True

    from robotparser import RobotFileParser
    RobotFileParser.can_fetch = my_can_fetch
