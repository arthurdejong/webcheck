
# http.py - handle urls with a http scheme
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk) <marduk@python.net>
# Copyright (C) 2002 Mike Meyer <mwm@mired.org>
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

"""This module defines the functions needed for creating Link objects for urls
using the http scheme"""

import myUrlLib
import string
import httplib
import urllib
import time
import urlparse
import base64
import mimetypes
import debugio
import version
import config

Link = myUrlLib.Link
proxies = config.PROXIES
if proxies is None:
    proxies = urllib.getproxies()

opener = urllib.FancyURLopener(proxies)
opener.addheaders = [('User-agent','webcheck ' + version.webcheck)]
if config.HEADERS:
    opener.addheaders = opener.addheaders + config.HEADERS

def _get_reply(url,redirect_depth=0):
    """Open connection to url and report information given by HEAD command"""

    (scheme,location,path,query,fragment)=urlparse.urlsplit(url)
    if proxies and proxies.has_key('http'):
        host = urlparse.urlparse(proxies['http'])[1]
        document = url
    else:
        host = location
        document = string.join((path,query),'')

    if not document:
        document = '/'
    debugio.debug('document=%s' % document)

    (username, passwd, realhost, port) = parse_host(host)

    if port:
        h=httplib.HTTPConnection(realhost,port)
    else:
        h=httplib.HTTPConnection(realhost)

    h.putrequest('HEAD', document)
    if username and passwd:
        auth = string.strip(base64.encodestring(username + ":" + passwd))
        h.putheader('Authorization', 'Basic %s' % auth)
    h.putheader('User-Agent','webcheck %s' % version.webcheck)
    h.endheaders()

    r = h.getresponse()
    errcode, errmsg, headers = r.status, r.reason, r.msg
    h.close()
    debugio.debug(errcode)
    debugio.debug(errmsg)
    if errcode == 301 or errcode == 302:
        if redirect_depth >= config.REDIRECT_DEPTH:
            debugio.error('  Too many redirects!')
            return (errcode, errmsg, headers, url)
        redirect = headers['location']
        debugio.info('  redirected to: ' + redirect)
        redirect = urlparse.urljoin(url,redirect)
        if redirect == url:
            debugio.error('  redirect same as source: %s' % redirect)
            return (errcode, errmsg, headers, url)
        if Link.linkMap.has_key(redirect):
            link = Link.linkMap[redirect]
            return (link.status, link.message, link.headers, link.URL)
        return _get_reply(redirect,redirect_depth+1)
    return (errcode, errmsg, headers, url)

def init(link, url, parent):
    """ Here, link is a reference of the link object that is calling this
    pseudo-method"""

    (link.status, link.message, link.headers, link.URL) = _get_reply(myUrlLib.basejoin(parent,url))
    Link.linkMap[link.URL] = link
    try:
        link.type = link.headers.gettype()
    except AttributeError:
        link.type = 'text/html' # is this a good enough default?

    debugio.debug('  Content-type: ' + link.type)
    try:
        link.size = int(link.headers['content-length'])
    except (KeyError, TypeError):
        link.size = 0

    if (link.status != 200) and (link.status != 'Not Checked'):
        link.set_bad_link(link.URL,str(link.status) + ": " +  link.message)
        return

    try:
        lastMod = time.mktime(link.headers.getdate('Last-Modified'))
    except (OverflowError, TypeError, ValueError):
        lastMod = None
    if lastMod:
        link.age = int((time.time()-lastMod)/myUrlLib.SECS_PER_DAY)

def get_document(url):
    document = opener.open(url).read()
    opener.cleanup()
    return document

def parse_host(location):
    """Return a tuple (user, password, host, port)
       
       takes string http://user:password@hostname:hostport and
       returns a tuple.  If a field is null in the string it will be
       returned as None in the tuple.
    """

    #location = urlparse.urlparse(host)[1]
    debugio.debug("network location= %s" % location)

    at = string.find(location, "@")
    if at > -1:
        userpass = location[:at]
        colon = string.find(userpass, ":")
        if colon > -1:
            user = userpass[:colon]
            passw = userpass[colon+1:]
        else:
            user = userpass
            passw = None
        hostport = location[at+1:]
    else:
        user = passw = None
        hostport = location

    colon = string.find(hostport, ":")
    if colon > -1:
        hostname = hostport[:colon]
        port = hostport[colon+1:]
    else:
        hostname = hostport
        port = None

    debugio.debug("parse_host = %s %s %s %s" % (user, passw, hostname, port))
    return (user, passw, hostname, port)
