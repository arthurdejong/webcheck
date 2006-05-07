
# ftp.py - handle urls with a ftp scheme
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
# Copyright (C) 2005, 2006 Arthur de Jong
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

"""This module defines the functions needed for creating Link objects for urls
using the ftp scheme."""

import config
import urllib
import mimetypes
import ftplib
import urlparse
import debugio

# FIXME: honor ftp proxy settings

# TODO: figure out a nicer way to close the connections with something like:
#try:
#    debugio.debug('FTP: '+ftp.quit())
#except:
#    debugio.debug('FTP: '+ftp.close())
# TODO: handle some exceptions earlier or use different commands

# a map of netlocs to ftp connections
_ftpconnections = {}

def _getconnection(netloc):
    """Return a FTP connection object to the specified server."""
    # NOTE: this method is not thread safe
    if _ftpconnections.has_key(netloc):
        return _ftpconnections[netloc]
    # split url into useful parts
    (userpass, host) = urllib.splituser(netloc)
    if userpass is not None:
        (user, passwd) = urllib.splitpasswd(userpass)
    else:
        (user, passwd) = ('anonymous', '')
    (host, port) = urllib.splitnport(host, ftplib.FTP_PORT)
    # initialize a new connection
    ftp = ftplib.FTP()
    debugio.debug('schemes.ftp._getconnection(): CONNECT: '+ftp.connect(host, port))
    debugio.debug('schemes.ftp._getconnection(): LOGIN: '+ftp.login(user, passwd))
    _ftpconnections[netloc] = ftp
    return ftp

def _cwd(ftp, path):
    """Go down the path on the ftp server returning the part that cannot be
    changed into."""
    # split the path into directories
    dirs = path.split('/')
    try:
        # decend down the tree
        while len(dirs) > 0:
            d = dirs[0]
            if d != '':
                debugio.debug('schemes.ftp._cwd(): CWD '+d+': '+ftp.cwd(d))
            dirs.pop(0)
        return None
    except ftplib.error_perm, e:
        debugio.debug('schemes.ftp._cwd(): CWD '+d+': '+str(e))
        return '/'.join(dirs)

def _fetch_directory(link, ftp, acceptedtypes):
    """Handle the ftp directory."""
    # check that the url ends with a slash
    if link.path[-1:] != '/':
        debugio.debug('schemes.ftp._fetch_directory(): directory referenced without trailing slash')
        link.redirect(urlparse.urljoin(link.url, link.path+'/'))
        return None
    # retreive the contents of the directory
    # FIXME: this raises an exception for empty directories, probably replace with own command
    contents = ftp.nlst()
    # check contents of directory for some common files
    for f in config.FTP_INDEXES:
        if f in contents:
            debugio.debug('schemes.ftp._fetch_directory(): pick up %s from directory' % f)
            # the the directory contains an index.html, use that
            return _fetch_file(link, ftp, f, acceptedtypes)
    # just add files in directory as children
    debugio.debug('schemes.ftp._fetch_directory(): add files as children of this page')
    link.ispage = True
    debugio.debug('schemes.ftp._fetch_directory(): TYPE A: '+ftp.voidcmd('TYPE A'))
    # FIXME: this raises an exception for empty directories
    for f in contents:
        link.add_child(urlparse.urljoin(link.url, urllib.quote(f)))
    return None

def _fetch_file(link, ftp, path, acceptedtypes):
    """Try to download the file in path that should be in the current
    directory of the ftp instance. The path can also point to a non-existant
    file or directory."""
    # figure out the size of the document
    link.size = ftp.size(path)
    debugio.debug('schemes.ftp.fetch(): size='+str(link.size))
    # guess the mimetype of the document
    if link.mimetype is None:
        link.mimetype = mimetypes.guess_type(path)[0]
    # try to fetch file
    if link.mimetype in acceptedtypes:
        debugio.debug('schemes.ftp.fetch(): TYPE I: '+ftp.voidcmd('TYPE I'))
        (conn, size) = ftp.ntransfercmd('RETR ' + path)
        if size:
            content = conn.makefile().read(size)
        else:
            content = conn.makefile().read()
        debugio.debug('schemes.ftp.fetch(): fetched, size=%d' % len(content))
        return content
    return None

def fetch(link, acceptedtypes):
    """Fetch the specified link."""
    # try to fetch the document
    try:
        ftp = _getconnection(link.netloc)
        debugio.debug('schemes.ftp.fetch(): CWD /: '+ftp.cwd('/'))
        # descend down the directory tree as far as we can go
        path = urllib.unquote(link.path)
        path = _cwd(ftp, path)
        # check if we are dealing with an (exising) directory
        if path is None:
            return _fetch_directory(link, ftp, acceptedtypes)
        else:
            return _fetch_file(link, ftp, path, acceptedtypes)
    except ftplib.all_errors, e:
        debugio.debug('schemes.ftp.fetch(): CAUGHT '+str(e))
        link.add_linkproblem(str(e))
        return None
