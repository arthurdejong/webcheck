
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
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

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

config = myUrlLib.config
Link = myUrlLib.Link
proxies = config.PROXIES
if proxies is None:
    proxies = urllib.getproxies()
redirect_depth = 0

opener = urllib.FancyURLopener(proxies)
opener.addheaders = [('User-agent','Webcheck ' + version.webcheck)]
if config.HEADERS:
    opener.addheaders = opener.addheaders + config.HEADERS

def get_reply(url):
    """Open connection to url and report information given by HEAD command"""

    global redirect_depth
    (scheme,location,path,query,fragment)=urlparse.urlsplit(url)
    if proxies and proxies.has_key('http'):
        host = urlparse.urlparse(proxies['http'])[1]
        document = url
    else:
        host = location
        document = string.join((path,query),'')

    if not document:
        document = '/'
    debugio.write('document=%s' % document,3)

    (username, passwd, realhost, port) = parse_host(host)

    if port:
        h=httplib.HTTPConnection(realhost,port)
    else:
        h=httplib.HTTPConnection(realhost)

    h.putrequest('HEAD', document)
    if username and passwd:
        auth = string.strip(base64.encodestring(username + ":" + passwd))
        h.putheader('Authorization', 'Basic %s' % auth)
    h.putheader('User-Agent','Webcheck %s' % version.webcheck)
    h.endheaders()

    r = h.getresponse()
    errcode, errmsg, headers = r.status, r.reason, r.msg
    h.close()
    debugio.write(errcode,2)
    debugio.write(errmsg,2)
    if errcode == 301 or errcode == 302:
        redirect_depth += 1
        if redirect_depth > config.REDIRECT_DEPTH:
            debugio.write('  Too many redirects!')
            redirect_depth = 0
            return (errcode, errmsg, headers, url)
        redirect = headers['location']
        debugio.write('  Redirect location: ' + redirect)
        redirect = urlparse.urljoin(url,redirect)
        if redirect == url:
            debugio.write('  Redirect same as source: %s' % redirect)
            redirect_depth = 0
            return (errcode, errmsg, headers, url)
        debugio.write('  Redirected to: ' + redirect)
        if Link.linkList.has_key(redirect):
            link = Link.linkList[redirect]
            return (link.status, link.message, link.headers, link.URL)
        return get_reply(redirect)
    redirect_depth = 0
    return (errcode, errmsg, headers, url)

def init(self, url, parent):
    """ Here, self is a reference of the link object that is calling this
    pseudo-method"""

    (self.status, self.message, self.headers, self.URL) = get_reply(myUrlLib.basejoin(parent,url))
    Link.linkList[self.URL] = self
    try:
        self.type = self.headers.gettype()
    except AttributeError:
        self.type = 'text/html' # is this a good enough default?

    debugio.write('  Content-type: ' + self.type,2)
    try:
        self.size = int(self.headers['content-length'])
    except (KeyError, TypeError):
        self.size = 0

    if (self.status != 200) and (self.status != 'Not Checked'):
        self.set_bad_link(self.URL,str(self.status) + ": " +  self.message)
        return

    try:
        lastMod = time.mktime(self.headers.getdate('Last-Modified'))
    except (OverflowError, TypeError, ValueError):
        lastMod = None
    if lastMod:
        self.age = int((time.time()-lastMod)/myUrlLib.SECS_PER_DAY)

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
    debugio.write("network location= %s" % location,3)

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

    debugio.write("parse_host = %s %s %s %s" % (user, passw, hostname, port),3)
    return (user, passw, hostname, port)
    
