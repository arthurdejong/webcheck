
# serialize.py - module for (de)serializing site data
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

"""This module is used for (de)serializing site data.

Serialization takes place to a file and can be done incremental.
The format of the serialized data is subject to change as this
format is currently experimental. The current format
is as follows:

internal_url*=URL
internal_re*=REGEXP
external_re*=REGEXP
yanked_re*=REGEXP

[URL]
child*=URL
embed*=URL
anchor*=ANCHOR
reqanchor*=PARENTURL|ANCHOR
isfetched=BOOL
ispage=BOOL
mtime=TIME
size=SIZE
mimetype=MIMETYPE
encoding=ENCODING
title=TITLE
author=AUTHOR
status=STATUS
linkproblem*=LEV;LINKPROBLEM
pageproblem*=LEV;PROBLEM
redirectdepth=NUM

When there are section name clashes earlier sections should be
ignored. Keys with * can be specified multiple times. This denotes
a list.
"""

import re
import time
import debugio
import parsers.html

# TODO: maybe save some part of configuration
# TODO: maybe also serialize robotparsers
# TODO: maybe serialize isyanked

# pattern for matching sections
_sectionpattern = re.compile('^\[(.+)\] *$')

# pattern for matching key-value pairs
_keyvaluepattern = re.compile('^([a-z0-9_-]+) *= *(.*)$')

# pattern for matching comments
_commentpattern = re.compile('^[;#]')

# pattern for splitting comma separated list
_commapattern = re.compile(',? *("[^"]*")')

# exception class
class DeSerializeException(Exception):
    """An exception class signalling a problem in parsing some
    value."""
    pass

# functions for writing data to the serialized file

def _escape(txt):
    """Escape the string to make it fit for writing to the serialized
    data file. The string is html escaped and surrounded by quotes."""
    return '"'+parsers.html.htmlescape(txt, True)+'"'

def _writebool(fp, key, value):
    """Write a key/value pair displaying a boolean."""
    if value is None:
        fp.write('%(key)s = None\n' % locals());
    elif value:
        fp.write('%(key)s = True\n' % locals());
    else:
        fp.write('%(key)s = False\n' % locals());

def _writeint(fp, key, value):
    """Write a key/value pair displaying an integer."""
    value = str(value)
    fp.write('%(key)s = %(value)s\n' % locals())

def _writestring(fp, key, value):
    """Write a key/value pair displaying a string or None."""
    if value is None:
        value = 'None'
    else:
        value = _escape(value)
    fp.write('%(key)s = %(value)s\n' % locals())

def _writedate(fp, key, value):
    """Write a key/value pair displaying a date value or None."""
    if value:
        date = time.strftime('%c %Z', time.localtime(value))
        fp.write('%(key)s = %(date)s\n' % locals())
    else:
        fp.write('%(key)s = None\n' % locals())

def _writelist(fp, key, values):
    """Write a comma separated list of string using proper
    quoting and html escaping."""
    value = ', '.join([ _escape(x) for x in values ])
    fp.write('%(key)s = %(value)s\n' % locals())

# functions for reading data from the serialized file

def _unescape(txt):
    """This function unescapes a quoted escaped string.
    The function removed quotes and replaces html entities
    with their proper values."""
    # strip quotes
    if txt[0] != '"' or txt[-1] != '"':
        raise DeSerializeException('parse error')
    txt = txt[1:-1]
    # unescape
    return parsers.html.htmlunescape(txt)

def _readbool(txt):
    """Interpret the string as a boolean value."""
    txt = txt.lower().strip()
    if txt in ('true', '1', '-1', 'yes', 'on'):
        return True
    elif txt in ('false', '0', 'no', 'off'):
        return False
    elif txt == 'none':
        return None
    else:
        raise DeSerializeException('parse error')

def _readint(txt):
    """Interpret the string as an integer value."""
    if txt == 'None':
        return None
    return int(txt)

def _readstring(txt, useunicode=True):
    """Transform the string read from a key/value pair
    to a string that can be used."""
    if txt == 'None':
        return None
    if useunicode:
        return _unescape(txt)
    else:
        return str(_unescape(txt))

def _readdate(txt):
    """Interpret the string as a date value."""
    import rfc822
    date = rfc822.parsedate_tz(txt.strip())
    if date is not None:
        return rfc822.mktime_tz(date)
    return None

def _readlist(txt):
    """nterpret the string as a list of strings."""
    return [ _readstring(x.strip())
             for x in _commapattern.findall(txt) ]

# general serialize and deraserialize functions

def serialize_site(fp, site):
    """Store the information of the site in the specified file."""
    for url in site._internal_urls:
        _writestring(fp, 'internal_url', url)
    for res in site._internal_res.keys():
        _writestring(fp, 'internal_re', res)
    for res in site._external_res.keys():
        _writestring(fp, 'external_re', res)
    for res in site._yanked_res.keys():
        _writestring(fp, 'yanked_re', res)
    fp.write('\n')

def serialize_links(fp, site):
    """Store all the links of the site in the specified file."""
    for link in site.linkMap.values():
        serialize_link(fp, link)

def serialize_link(fp, link):
    """Store the information on the url in the specified file."""
    fp.write('[%s]\n' % link.url)
    if link.isfetched:
        _writebool(fp, 'isfetched', link.isfetched)
    if link.isfetched:
        _writebool(fp, 'ispage', link.ispage)
    if link.mtime:
        _writedate(fp, 'mtime', link.mtime)
    if link.size:
        _writeint(fp, 'size', link.size)
    if link.mimetype:
        _writestring(fp, 'mimetype', link.mimetype)
    if link.encoding:
        _writestring(fp, 'encoding', link.encoding)
    if link.title:
        _writestring(fp, 'title', link.title)
    if link.author:
        _writestring(fp, 'author', link.author)
    if link.status:
        _writestring(fp, 'status', link.status)
    if link.redirectdepth > 0:
        _writeint(fp, 'redirectdepth', link.redirectdepth)
    for child in link.children:
        _writestring(fp, 'child', child.url)
    for embed in link.embedded:
        _writestring(fp, 'embed', embed.url)
    for anchor in link.anchors:
        _writestring(fp, 'anchor', anchor)
    for reqanchor in link.reqanchors:
        for parent in link.reqanchors[reqanchor]:
            _writelist(fp, 'reqanchor', (parent.url, reqanchor))
    for problem in link.linkproblems:
        _writestring(fp, 'linkproblem', problem)
    for problem in link.pageproblems:
        _writestring(fp, 'pageproblem', problem)
    fp.write('\n')

def _deserialize_site(site, key, value):
    """The data in the key value pair is fed into the site."""
    debugio.debug("%s=%s" % (key, value))
    if key == 'internal_url':
        site.add_internal(_readstring(value, False))
    elif key == 'internal_re':
        site.add_internal_re(_readstring(value))
    elif key == 'external_re':
        site.add_external_re(_readstring(value))
    elif key == 'yanked_re':
        site.add_yanked_re(_readstring(value))
    else:
        raise DeSerializeException('parse error')

def _deserialize_link(link, key, value):
    """The data in the kay value pair is fed into the link."""
    link._ischanged = True
    if key == 'child':
        link.add_child(_readstring(value, False))
    elif key == 'embed':
        link.add_embed(_readstring(value, False))
    elif key == 'anchor':
        link.add_anchor(_readstring(value, False))
    elif key == 'reqanchor':
        (url, anchor) = _readlist(value)
        link.add_reqanchor(str(url), str(anchor))
    elif key == 'isfetched':
        link.isfetched = _readbool(value)
    elif key == 'ispage':
        link.ispage = _readbool(value)
    elif key == 'mtime':
        link.mtime = _readdate(value)
    elif key == 'size':
        link.size = _readint(value)
    elif key == 'mimetype':
        link.mimetype = _readstring(value, False)
    elif key == 'encoding':
        link.encoding = _readstring(value, False)
    elif key == 'title':
        link.title = _readstring(value)
    elif key == 'author':
        link.author = _readstring(value)
    elif key == 'status':
        link.status = _readstring(value, False)
    elif key =='linkproblem':
        link.add_linkproblem(_readstring(value, False))
    elif key =='pageproblem':
        link.add_pageproblem(_readstring(value, False))
    elif key == 'redirectdepth':
        link.redirectdepth = _readint(value)
    else:
        raise DeSerializeException('parse error')

def deserialize(fp):
    """Read data from the file and construct objects from it.
    A new site instance is returned.
    After the site has been deserialized the crawl() and postprocess()
    functions should be called to regenerate the other link attributes."""
    import crawler
    site = crawler.Site()
    link = None
    while True:
        line = fp.readline()
        # check for end-of-file
        if not line:
            break
        # skip comments
        if _commentpattern.search(line):
            continue
        # skip empty lines
        if line.rstrip() == '':
            continue
        # find section header
        match = _sectionpattern.search(line)
        if match:
            link = site.get_link(match.group(1))
            debugio.info('  %s' % link.url)
            # clear some data that is annoying if we have duplicates
            link.anchors = []
            link.linkproblems = []
            link.pageproblems = []
            continue
        # check for key-value pair
        match = _keyvaluepattern.search(line)
        if match:
            key = match.group(1)
            value = match.group(2)
            if link is None:
                _deserialize_site(site, key, value)
            else:
                _deserialize_link(link, key, value)
            continue
        # fallthrough
        raise DeSerializeException('parse error')
    return site
