
# html.py - parser functions for html content
#
# Copyright (C) 2007 Arthur de Jong
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

"""Parser functions for processing HTML content. This module uses the
BeautifulSoup HTML parser and is more flexible than the legacy HTMLParser
module."""

import urlparse
import crawler
import re
import htmlentitydefs
import BeautifulSoup
from parsers.html import htmlunescape

def parse(content, link):
    """Parse the specified content and extract an url list, a list of images a
    title and an author. The content is assumed to contain HMTL."""
    # create parser and feed it the content
    soup = BeautifulSoup.BeautifulSoup(content,
                                       fromEncoding=str(link.encoding))
    # fetch document encoding
    link.set_encoding(soup.originalEncoding)
    # <title>TITLE</title>
    title = soup.find('title')
    if title and title.string:
        link.title = htmlunescape(title.string).strip()

    # FIXME: using crawler.urlescape is wrong below, we should probably use
    #        something like link.urlunescape() to do the escaping and check
    #        and log at the same time

    # <base href="URL">
    base = soup.find('base', href=True)
    if base:
        base = crawler.urlescape(htmlunescape(base['href']).strip())
    else:
        base = link.url
    # <link rel="TYPE" href="URL">
    for l in soup.findAll('link', rel=True, href=True):
        if l['rel'].lower() in ('stylesheet', 'alternate stylesheet', 'icon', 'shortcut icon'):
            embed = crawler.urlescape(htmlunescape(l['href']).strip())
            if embed:
                link.add_embed(urlparse.urljoin(base, embed))
    # <meta name="author" content="AUTHOR">
    author = soup.find('meta', attrs={'name': re.compile("^author$", re.I), 'content': True})
    if author and author.string:
        link.author = crawler.urlescape(htmlunescape(author.string).strip())
    # <meta http-equiv="refresh" content="0;url=URL">
    refresh = soup.find('meta', attrs={'http-equiv': re.compile("^refresh$", re.I), 'content': True})
    if refresh:
        pass # TODO: implement
    # <img src="URL">
    for img in soup.findAll('img', src=True):
        embed = crawler.urlescape(htmlunescape(img['src']).strip())
        if embed:
            link.add_embed(urlparse.urljoin(base, embed))
    # <a href="URL">
    for a in soup.findAll('a', href=True):
        child = crawler.urlescape(htmlunescape(a['href']).strip())
        if child:
            link.add_child(urlparse.urljoin(base, child))
    # <a name="NAME">
    # TODO: consistent url escaping?
    for a in soup.findAll('a', attrs={'name': True}):
        # get anchor name
        a_name = crawler.urlescape(htmlunescape(a['name']).strip())
        # if both id and name are used they should be the same
        if a.has_key('id') and a_name != crawler.urlescape(htmlunescape(a['id']).strip()):
            link.add_pageproblem(
              'anchors defined in name and id attributes do not match')
            # add the id anchor anyway
            link.add_anchor(crawler.urlescape(htmlunescape(a['id']).strip()))
        # add the anchor
        link.add_anchor(a_name)
    # <a id="ID">
    for a in soup.findAll('a', id=True):
        # skip entries that have a name
        if a.has_key('name'):
            continue
        # add the anchor
        link.add_anchor(crawler.urlescape(htmlunescape(a['id']).strip()))
    # <frameset><frame src="URL"...>...</frameset>
    for frame in soup.findAll('frame', src=True):
        embed = crawler.urlescape(htmlunescape(frame['src']).strip())
        if embed:
            link.add_embed(urlparse.urljoin(base, embed))
    # <map><area href="URL"...>...</map>
    for area in soup.findAll('area', href=True):
        child = crawler.urlescape(htmlunescape(area['href']).strip())
        if child:
            link.add_child(urlparse.urljoin(base, child))
    # <applet code="URL" [archive="URL"]...>
    for applet in soup.findAll('applet', code=True):
        # if applet has archive tag check that
        if applet.has_key('archive'):
            embed = crawler.urlescape(htmlunescape(applet['archive']).strip())
        else:
            embed = crawler.urlescape(htmlunescape(applet['code']).strip())
        if embed:
            link.add_embed(urlparse.urljoin(base, embed))
    # <embed src="URL"...>
    for embedd in soup.findAll('frame', src=True):
        embed = crawler.urlescape(htmlunescape(embedd['src']).strip())
        if embed:
            link.add_embed(urlparse.urljoin(base, embed))
    # <embed><param name="movie" value="url"></embed>
    for param in soup.findAll('param', attrs={'name': re.compile("^movie$", re.I), 'value': True}):
        embed = crawler.urlescape(htmlunescape(param['value']).strip())
        if embed:
            link.add_embed(urlparse.urljoin(base, embed))
    # <style>content</style>
    for style in soup.findAll('style', src=True):
        if style.string:
            # delegate handling of inline css to css module
            import parsers.css
            parsers.css.parse(htmlunescape(style.string), link)
    # flag that the link contains a valid page
    link.ispage = True
