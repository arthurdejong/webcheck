
# http.py - handle urls with a http scheme
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

"""This module defines the functions needed for filling in information in Link
objects for urls using the http scheme."""

import config
import debugio
import string
import httplib
import urllib
import time
import urlparse
import base64
import socket

def fetch(link):
    """Open connection to url and report information given by GET command."""
    # TODO: HTTP connection pooling?
    # split netloc in user:pass part and host:port part
    (userpass,netloc) = urllib.splituser(link.netloc)
    host = urllib.splitport(netloc)[0]
    # check which host to connect to (if using proxies)
    if config.PROXIES and config.PROXIES.has_key(link.scheme):
        # pass the complete url in the request, connecting to the proxy
        # TODO: implement proxy authentication
        path = urlparse.urlunsplit((link.scheme,netloc,link.path,link.query,""))
        netloc = urlparse.urlsplit(config.PROXIES[link.scheme])[1]
    else:
        # otherwise direct connect to the server with partial url
        path = urlparse.urlunsplit(("","",link.path,link.query,""))
    conn=None
    try:
        try:
            # create the connection
            if link.scheme == "http":
                conn=httplib.HTTPConnection(netloc)
            elif link.scheme == "https":
                conn=httplib.HTTPSConnection(netloc)
            # the requests adds a correct host header for us
            conn.putrequest("GET", path)
            if userpass is not None:
                (user, passwd) = urllib.splitpasswd(userpass)
                conn.putheader("Authorization", "Basic "+string.strip(base64.encodestring(user + ":" + passwd)))
            conn.putheader("User-Agent","webcheck %s" % config.VERSION)
            conn.endheaders()
            # wait for the response
            response = conn.getresponse()
            debugio.debug("schemes.http.fetch(): HTTP response: %s %s" % (response.status, response.reason))
            # retrieve some information from the headers
            try:
                link.mimetype = response.msg.gettype()
                debugio.debug("schemes.http.fetch(): mimetype: %s" % str(link.mimetype))
            except AttributeError:
                pass
            try:
                link.size = int(response.getheader("Content-length"))
                debugio.debug("schemes.http.fetch(): size: %s" % str(link.size))
            except (KeyError, TypeError):
                pass
            try:
                link.mtime = time.mktime(response.msg.getdate("Last-Modified"))
                debugio.debug("schemes.http.fetch(): mtime: %s" % time.strftime("%c",time.localtime(link.mtime)))
            except (OverflowError, TypeError, ValueError):
                pass
            # handle redirects
            # 301=moved permanently, 302=found, 303=see other, 307=temporary redirect
            if response.status == 301 or response.status == 302 or response.status == 303 or response.status == 307:
                # consider a 301 (moved permanently) a problem
                if response.status == 301:
                    link.add_problem(str(response.status) + ": " +  response.reason)
                # determin depth
                redirectdepth = 0
                for p in link.parents:
                    redirectdepth = max(redirectdepth,p.redirectdepth)
                link.redirectdepth = redirectdepth + 1
                # check depth
                if link.redirectdepth >= config.REDIRECT_DEPTH:
                    link.add_problem("too many redirects (%d)" % link.redirectdepth)
                    return None
                # find url that is redirected to
                location = urlparse.urljoin(link.url,response.getheader("Location",""))
                if location == link.url:
                    link.add_problem("redirect same as source: %s" % location)
                    return None
                # add child
                link.add_child(location)
                return None
                # FIXME: add check for redirect loop detection
            elif response.status != 200:
                # handle error responses
                link.add_problem(str(response.status) + ": " +  response.reason)
                return None
            else:
                # return succesful responses
                # TODO: support gzipped content
                return response.read()
        except httplib.BadStatusLine, e:
            link.add_problem("error reading HTTP response: "+str(e))
            return None
        except socket.error, (errnr,errmsg):
            link.add_problem("error reading HTTP response: "+errmsg)
            return None
    finally:
        # close the connection before returning
        if conn is not None:
            conn.close()
