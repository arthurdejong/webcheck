
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
# FIXME: keep connection open and only close after we're done

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
    path=urllib.unquote(path)
    return (host, port, user, passwd, path)

def _cwd(ftp, path):
    """Go down the path on the ftp server returning the part that cannot be
    changed into."""
    # split the path into directories
    dirs = path.split('/')
    try:
        # decend down the tree
        while len(dirs) > 0:
            d = dirs[0]
            debugio.debug("FTP: "+ftp.cwd(d))
            dirs.pop(0)
        return None
    except ftplib.error_perm:
        return string.join(dirs,'/')

def fetch(link, acceptedtypes):
    """Fetch the specified link."""
    # split url into useful parts
    (host, port, user, passwd, path) = _spliturl(link.url)
    # try to fetch the document
    content = None
    try:
        ftp = ftplib.FTP()
        debugio.debug("FTP: "+ftp.connect(host, port))
        debugio.debug("FTP: "+ftp.login(user, passwd))
        debugio.debug("FTP: "+ftp.voidcmd('TYPE I'))
        # descend down the directory tree as far as we can go
        path=_cwd(ftp, path)
        # check if we are dealing with an (exising) directory
        if path is None:
            # check that the url ends with a slash
            if link.path[-1:] != '/':
                debugio.debug('directory referenced without trailing slash')
                link.redirectdepth = 1
                link.add_child(urlparse.urljoin(link.url,link.path+'/'))
            else:
                # add children
                debugio.debug('add files as children of this page')
                link.ispage = True
                for f in ftp.nlst():
                    link.add_child(urlparse.urljoin(link.url,urllib.quote(f)))
        else:
            # figure out the size of the document
            link.size = ftp.size(path)
            # guess the mimetype of the document
            if link.mimetype is None:
                link.mimetype = mimetypes.guess_type(path)[0]
            # try to fetch file
            if link.mimetype in acceptedtypes:
                (conn, size) = ftp.ntransfercmd('RETR ' + path)
                if size:
                   content = conn.makefile().read(size)
                else:
                   content = conn.makefile().read()
    except ftplib.all_errors, e:
        link.add_problem(str(e))
    # finally close the ftp connection
    try:
        debugio.debug("FTP: "+ftp.quit())
    except:
        debugio.debug("FTP: "+ftp.close())
    # we're done
    return content
