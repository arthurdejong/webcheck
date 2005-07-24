
# http.py - handle urls with a http scheme
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk) <marduk@python.net>
# Copyright (C) 2002 Mike W. Meyer <mwm@mired.org>
# Copyright (C) 2005 Arthur de Jong <arthur@tiefighter.et.tudelft.nl>
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

# http://www.ietf.org/rfc/rfc2616.txt

import string
import httplib
import urllib
import time
import urlparse
import base64
import mimetypes
import debugio
import config

opener = urllib.FancyURLopener(config.PROXIES)
opener.addheaders = [('User-agent','webcheck ' + config.VERSION)]
if config.HEADERS:
    opener.addheaders = opener.addheaders + config.HEADERS

def _get_reply(link):
    """Open connection to url and report information given by HEAD command."""
    if config.PROXIES and config.PROXIES.has_key('http'):
        host = urlparse.urlparse(config.PROXIES['http'])[1]
        path = link.url
    else:
        host = link.netloc
        path = string.join((link.path,link.query),'')
    if not path:
        path = '/'
    userpass = urllib.splituser(link.netloc)[0]
    if userpass is None:
        (user, passwd) = (None, None)
    else:
        (user, passwd) = urllib.splitpasswd(userpass)
    (host, port) = urllib.splitport(host)
    if port:
        h=httplib.HTTPConnection(host,port)
    else:
        h=httplib.HTTPConnection(host)
    h.putrequest('HEAD', path)
    if user and passwd:
        auth = string.strip(base64.encodestring(user + ":" + passwd))
        h.putheader('Authorization', 'Basic %s' % auth)
    h.putheader('User-Agent','webcheck %s' % config.VERSION)
    h.endheaders()
    try:
        r = h.getresponse()
        errcode, errmsg, headers = r.status, r.reason, r.msg
        h.close()
        debugio.debug("HTTP response: %s %s" % (errcode, errmsg))
    except httplib.BadStatusLine, e:
        return (-1, "error reading HTTP response: "+str(e),[])
    # handle redirects
    #  301 = moved permanently
    #  302 = found
    #  303 = see other
    #  307 = temporary redirect
    if errcode == 301 or errcode == 302 or errcode == 303 or errcode == 307:
        # TODO: consider pages linking to 301 (moved permanently) an error
        # determin depth
        redirectdepth = 0
        for p in link.parents:
            redirectdepth = max(redirectdepth,p.redirectdepth)
        link.redirectdepth = redirectdepth + 1
        # check depth
        if link.redirectdepth >= config.REDIRECT_DEPTH:
            debugio.error("too many redirects")
            return (errcode, errmsg, headers)
        # find url that is redirected to
        location = headers['location']
        debugio.info('    redirected to: ' + location)
        location = urlparse.urljoin(link.url,location)
        if location == link.url:
            debugio.error("redirect same as source: %s" % location)
            return (errcode, errmsg, headers)
        # add child
        link.add_child(location)
        # TODO: add check for redirect loop detection
    return (errcode, errmsg, headers)

def fetch(link):
    """Here, link is a reference of the link object that is calling this
    pseudo-method."""
    (status, message, headers) = _get_reply(link)
    try:
        link.mimetype = headers.gettype()
    except AttributeError:
        link.mimetype = 'text/html' # is this a good enough default?
    debugio.debug('content-type: ' + link.mimetype)
    try:
        link.size = int(headers['content-length'])
    except (KeyError, TypeError):
        link.size = 0
    debugio.debug('size: ' + str(link.size))
    if (status != 200):
        link.add_problem(str(status) + ": " +  message)
        return
    try:
        link.mtime = time.mktime(headers.getdate('Last-Modified'))
    except (OverflowError, TypeError, ValueError):
        pass
    document = opener.open(link.url).read()
    opener.cleanup()
    return document
