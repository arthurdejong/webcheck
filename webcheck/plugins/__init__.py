
# __init__.py - plugin function module
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
# Copyright (C) 2005, 2006, 2007, 2009, 2011, 2013 Arthur de Jong
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

"""This package groups all the plugins.

When generating the report each plugin is called in turn with
the generate() function. Each plugin should export the following
fields:

    generate(crawler)
        Based on the site generate all the output files as needed.
    __title__
        A short description of the plugin that is used when linking
        to the output from the plugin.
    __author__
        The author(s) of the plugin.
    __outputfile__
        The file the plugin generates (for linking to).
    docstring
        The docstring is used as description of the plugin in the
        report.

Pluings can use the functions exported by this module."""

import time

from sqlalchemy.orm import joinedload

import webcheck
from webcheck import config
from webcheck.db import Link
from webcheck.parsers.html import htmlescape
from webcheck.util import open_file


def _floatformat(f):
    """Return a float as a string while trying to keep it within three
    characters."""
    txt = '%.1f' % f
    # remove period from too long strings
    if len(txt) > 3:
        txt = txt[:txt.find('.')]
    return txt


def get_size(i):
    """Return the size in bytes as a readble string."""
    K = 1024
    M = K * 1024
    G = M * 1024
    if i > 1024 * 1024 * 999:
        return _floatformat(float(i) / float(G)) + 'G'
    elif i > 1024 * 999:
        return _floatformat(float(i) / float(M)) + 'M'
    elif i >= 1024:
        return _floatformat(float(i) / float(K)) + 'K'
    else:
        return '%d' % i


def _get_info(link):
    """Return a string with a summary of the information in the link."""
    info = u'url: %s\n' % link.url
    if link.status:
        info += u'%s\n' % link.status
    if link.title:
        info += u'title: %s\n' % link.title.strip()
    if link.author:
        info += u'author: %s\n' % link.author.strip()
    if link.is_internal:
        info += u'internal link'
    else:
        info += u'external link'
    if link.yanked:
        info += u', not checked (%s)\n' % link.yanked
    else:
        info += u'\n'
    if link.redirectdepth:
        if link.children.count() > 0:
            info += u'redirect: %s\n' % link.children.first().url
        else:
            info += u'redirect (not followed)\n'
    count = link.count_parents
    if count == 1:
        info += u'linked from 1 page\n'
    elif count > 1:
        info += u'linked from %d pages\n' % count
    if link.mtime:
        info += u'last modified: %s\n' % time.ctime(link.mtime)
    if link.size:
        info += u'size: %s\n' % get_size(link.size)
    if link.mimetype:
        info += u'mime-type: %s\n' % link.mimetype
    if link.encoding:
        info += u'encoding: %s\n' % link.encoding
    for problem in link.linkproblems:
        info += u'problem: %s\n' % problem.message
    # trim trailing newline
    return info.strip()


def make_link(link, title=None):
    """Return an <a>nchor to a url with title. If url is in the Linklist and
    is external, insert "class=external" in the <a> tag."""
    return '<a href="%(url)s" %(target)sclass="%(cssclass)s" title="%(info)s">%(title)s</a>' % \
            dict(url=htmlescape(link.url),
                 target='target="_blank" ' if config.REPORT_LINKS_IN_NEW_WINDOW else '',
                 cssclass='internal' if link.is_internal else 'external',
                 info=htmlescape(_get_info(link)).replace('\n', '&#10;'),
                 title=htmlescape(title or link.title or link.url))


def print_parents(fp, link, indent='     '):
    """Write a list of parents to the output file descriptor.
    The output is indeted with the specified indent."""
    # if there are no parents print nothing
    count = link.count_parents
    if not count:
        return
    parents = link.parents.order_by(Link.title, Link.url).options(joinedload(Link.linkproblems))[:config.PARENT_LISTLEN]
    fp.write(
      indent + '<div class="parents">\n' +
      indent + ' referenced from:\n' +
      indent + ' <ul>\n')
    more = link.count_parents
    for parent in parents:
        fp.write(
          indent + '  <li>%(parent)s</li>\n'
          % {'parent': make_link(parent)})
        more -= 1
    if more:
        fp.write(
          indent + '  <li>%(more)d more...</li>\n'
          % {'more': more})
    fp.write(
      indent + ' </ul>\n' +
      indent + '</div>\n')


def _print_navbar(fp, selected, crawler):
    """Return an html fragement representing the navigation bar for a page."""
    fp.write('  <ul class="navbar">\n')
    for plugin in crawler.plugins:
        # skip if no outputfile
        if not hasattr(plugin, '__outputfile__'):
            continue
        # generate a link to the plugin page
        selected = ''
        if plugin == selected:
            selected = ' class="selected"'
        fp.write(
          '   <li><a href="%(pluginfile)s"%(selected)s title="%(description)s">%(title)s</a></li>\n'
          % {'pluginfile':  plugin.__outputfile__,
             'selected':    selected,
             'title':       htmlescape(plugin.__title__),
             'description': htmlescape(plugin.__doc__)})
    fp.write('  </ul>\n')


def open_html(plugin, crawler):
    """Print an html fragment for the start of an html page."""
    # open the file
    fp = open_file(plugin.__outputfile__)
    # get the first base url
    base = crawler.bases[0]
    # write basic html head
    fp.write(
      '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
      '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n'
      '<html xmlns="http://www.w3.org/1999/xhtml">\n'
      ' <head>\n'
      '  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />\n'
      '  <title>Webcheck report for %(sitetitle)s (%(plugintitle)s)</title>\n'
      '  <link rel="stylesheet" type="text/css" href="webcheck.css" />\n'
      '  <link rel="icon" href="favicon.ico" type="image/ico" />\n'
      '  <link rel="shortcut icon" href="favicon.ico" />\n'
      '  <script type="text/javascript" src="fancytooltips.js"></script>\n'
      '  <meta name="Generator" content="webcheck %(version)s" />\n'
      ' </head>\n'
      ' <body>\n'
      '  <h1 class="basename">Webcheck report for <a href="%(siteurl)s">%(sitetitle)s</a></h1>\n'
      % {'sitetitle':   htmlescape(base.title or base.url),
         'plugintitle': htmlescape(plugin.__title__),
         'siteurl':     base.url,
         'version':     webcheck.__version__})
    # write navigation bar
    _print_navbar(fp, plugin, crawler)
    # write plugin heading
    fp.write('  <h2>%s</h2>\n' % htmlescape(plugin.__title__))
    # write plugin contents
    fp.write('  <div class="content">\n')
    return fp


def close_html(fp):
    """Print an html fragment as footer of an html page."""
    fp.write('  </div>\n')
    # write bottom of page
    fp.write(
      '  <p class="footer">\n'
      '   Generated %(time)s by <a href="%(homepage)s">webcheck %(version)s</a>\n'
      '  </p>\n'
      ' </body>\n'
      '</html>\n'
      % {'time':     htmlescape(time.ctime(time.time())),
         'homepage': webcheck.__homepage__,
         'version':  htmlescape(webcheck.__version__)})
    fp.close()
