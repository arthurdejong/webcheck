
# http.py - handle urls with a http scheme
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

"""This module defines the functions needed for filling in information in Link
objects for urls using the http scheme."""

import config
import debugio
import httplib
import urllib
import time
import urlparse
import base64
import socket
import re

# pattern for extracting character set information from content-type header
_charsetpattern = re.compile('charset=([^ ]*)', re.I)

# set socket timeout to configured value
socket.setdefaulttimeout(config.IOTIMEOUT)

def fetch(link, acceptedtypes):
    """Open connection to url and report information given by GET command."""
    # TODO: HTTP connection pooling?
    # TODO: implement proxy requests for https
    # split netloc in user:pass part and host:port part
    (userpass, netloc) = urllib.splituser(link.netloc)
    proxyuserpass = None
    scheme = link.scheme
    # check which host to connect to (if using proxies)
    if config.PROXIES and config.PROXIES.has_key(link.scheme):
        # pass the complete url in the request, connecting to the proxy
        path = urlparse.urlunsplit((link.scheme, netloc, link.path, link.query, ''))
        (scheme, netloc) = urlparse.urlsplit(config.PROXIES[link.scheme])[0:2]
        (proxyuserpass, netloc) = urllib.splituser(netloc)
    else:
        # otherwise direct connect to the server with partial url
        path = urlparse.urlunsplit(('', '', link.path, link.query, ''))
    # remove trailing : from netloc
    if netloc[-1] == ':':
        netloc = netloc[:-1]
    conn = None
    try:
        try:
            # create the connection
            debugio.debug('schemes.http.fetch: connecting to %s' % netloc)
            if scheme == 'http':
                conn = httplib.HTTPConnection(netloc)
            elif scheme == 'https':
                conn = httplib.HTTPSConnection(netloc)
            # the requests adds a correct host header for us
            conn.putrequest('GET', path)
            if userpass is not None:
                (user, passwd) = urllib.splitpasswd(userpass)
                conn.putheader(
                  'Authorization',
                  'Basic '+base64.encodestring(str(user)+':'+str(passwd)).strip() )
            if proxyuserpass is not None:
                (user, passwd) = urllib.splitpasswd(proxyuserpass)
                conn.putheader(
                  'Proxy-Authorization',
                  'Basic '+base64.encodestring(str(user)+':'+str(passwd)).strip() )
            # bypass proxy cache
            if config.BYPASSHTTPCACHE:
                conn.putheader('Cache-control', 'no-cache')
                conn.putheader('Pragma', 'no-cache')
            conn.putheader('User-Agent','webcheck %s' % config.VERSION)
            conn.endheaders()
            # wait for the response
            response = conn.getresponse()
            link.status = '%s %s' % (response.status, response.reason)
            debugio.debug('schemes.http.fetch(): HTTP response: %s' % link.status)
            # dump proxy hit/miss debugging info
            if config.PROXIES and config.PROXIES.has_key(link.scheme):
                try:
                    debugio.debug('schemes.http.fetch(): X-Cache: %s' % str(response.getheader('X-Cache')))
                except AttributeError:
                    pass
            # retrieve some information from the headers
            try:
                link.mimetype = response.msg.gettype()
                debugio.debug('schemes.http.fetch(): mimetype: %s' % str(link.mimetype))
            except AttributeError:
                pass
            try:
                link.set_encoding(_charsetpattern.search(response.getheader('Content-type')).group(1))
            except (AttributeError, TypeError):
                pass
            try:
                link.size = int(response.getheader('Content-length'))
                debugio.debug('schemes.http.fetch(): size: %s' % str(link.size))
            except (KeyError, TypeError):
                pass
            try:
                link.mtime = time.mktime(response.msg.getdate('Last-Modified'))
                debugio.debug('schemes.http.fetch(): mtime: %s' % time.strftime('%c', time.localtime(link.mtime)))
            except (OverflowError, TypeError, ValueError):
                pass
            # handle redirects
            # 301=moved permanently, 302=found, 303=see other, 307=temporary redirect
            if response.status in (301, 302, 303, 307):
                # consider a 301 (moved permanently) a problem
                if response.status == 301:
                    link.add_linkproblem(str(response.status)+': '+response.reason)
                # find url that is redirected to
                location = urlparse.urljoin(link.url, response.getheader('Location', ''))
                # create the redirect
                link.redirect(location)
                return None
            elif response.status != 200:
                # handle error responses
                link.add_linkproblem(str(response.status)+': '+response.reason)
                return None
            elif link.mimetype in acceptedtypes:
                # return succesful responses
                # TODO: support gzipped content
                # TODO: add checking for size
                return response.read()
        except httplib.HTTPException, e:
            debugio.debug('error reading HTTP response: '+str(e))
            link.add_linkproblem('error reading HTTP response: '+str(e))
            return None
        except (socket.error, socket.sslerror), e:
            if hasattr(e, 'args') and len(e.args) == 2:
                debugio.debug("error reading HTTP response: "+str(e.args[1]))
                link.add_linkproblem("error reading HTTP response: "+str(e.args[1]))
            else:
                debugio.debug("error reading HTTP response: "+str(e))
                link.add_linkproblem("error reading HTTP response: "+str(e))
            return None
        except Exception, e:
            # handle all other exceptions
            debugio.debug('unknown exception caught: '+str(e))
            link.add_linkproblem('error reading HTTP response: '+str(e))
            import traceback
            traceback.print_exc()
            return None
    finally:
        # close the connection before returning
        if conn is not None:
            conn.close()
