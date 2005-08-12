
# ftp.py - handle urls with a ftp scheme
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
# Copyright (C) 2005 Arthur de Jong
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

"""This module defines the functions needed for creating Link objects for urls
using the ftp scheme."""

import urllib
import mimetypes
import ftplib
import urlparse
import string
import debugio

# FIXME: honor ftp proxy settings
# TODO: if browsing an FTP directory, also make it crawlable

def get_info(link):
    link.type = mimetypes.guess_type(link.url)[0]
    (host, port, user, passwd, path) = _spliturl(link.url)
    try:
        ftp = ftplib.FTP()
        ftp.connect(host, port)
        ftp.login(user, passwd)
        dirs, filename = _split_dirs(path)
        _cwd(dirs, ftp)
        if filename:
            try:  # FTP.size raises an exception instead of returning None!
                link.size = ftp.size(filename)
            except ftplib.error_perm:
                link.size = 0
                if filename not in ftp.nlst():
                    raise ftplib.error_perm, "No such file or directory"
    except ftplib.all_errors, e:
        link.add_problem(str(e))
    try:
        ftp.quit()
    except:
        ftp.close()

def _callback(line):
    """Read a line of text and do nothing with it"""
    return

def get_document(link):
    (host, port, user, passwd, path) = _spliturl(link.url)
    dirs, filename = _split_dirs(path)
    ftp = ftplib.FTP()
    ftp.connect(host, port)
    ftp.login(user, passwd)
    _cwd(dirs, ftp)
    ftp.voidcmd('TYPE I')
    conn, size = ftp.ntransfercmd('RETR ' + filename)
    if size:
       page = conn.makefile().read(size)
    else:
       page = conn.makefile().read()
    try:
       ftp.quit()
    except ftplib.all_errors:
       ftp.close()
    return page

def _split_dirs(path):
    """Given pathname, split it into a tuple consisting of a list of dirs and
    a filename"""
    dirs = map(urllib.unquote, string.split(path, '/'))
    filename = dirs.pop()
    if len(dirs) and not dirs[0]:
        del dirs[0]
    return (dirs, filename)

def _cwd(dirs, ftpobject):
    for dir in dirs:
        ftpobject.cwd(dir)

def _spliturl(url):
    """Split the specified url in host, port, user, password and path
    components, falling back to reasonable defaults for the ftp protocol."""
    (scheme, netloc, path, query, fragment) = urlparse.urlsplit(url)
    (userpass, host) = urllib.splituser(netloc)
    if userpass is not None:
        (user, passwd) = urllib.splitpasswd(userpass)
    else:
        (user, passwd) = ('anonymous', '')
    (host, port) = urllib.splitnport(host,ftplib.FTP_PORT)
    return (host, port, user, passwd, path)

def fetch(link, mimetypes):
    get_info(link)
    return get_document(link)
