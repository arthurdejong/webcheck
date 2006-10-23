
# __init__.py - plugin function module
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

"""This package groups all the plugins.

When generating the report each plugin is called in turn with
the generate() function. Each plugin should export the following
fields:

    generate(site)
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

import sys
import debugio
import config
import time
import parsers.html

# reference function from html module
htmlescape = parsers.html.htmlescape

def get_title(link):
    """Returns the title of a link if it is set otherwise returns url."""
    if link.title is None or link.title == '':
        return link.url
    return link.title

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
    M = K*1024
    G = M*1024
    if i > 1024*1024*999:
        return _floatformat(float(i)/float(G))+'G'
    elif i > 1024*999:
        return _floatformat(float(i)/float(M))+'M'
    elif i >= 1024:
        return _floatformat(float(i)/float(K))+'K'
    else:
        return '%d' % i

def get_info(link):
    """Return a string with a summary of the information in the link."""
    info = u'url: %s\n' % unicode(link.url, errors='replace')
    if link.status:
        info += '%s\n' % unicode(link.status, errors='replace')
    if link.title:
        info += 'title: %s\n' % link.title.strip()
    if link.author:
        info += 'author: %s\n' % link.author.strip()
    if link.isinternal:
        info += 'internal link'
    else:
        info += 'external link'
    if link.isyanked:
        if isinstance(link.isyanked, unicode):
            info += ', not checked (%s)\n' % link.isyanked
        if isinstance(link.isyanked, str):
            info += ', not checked (%s)\n' % unicode(link.isyanked, errors='replace')
        else:
            info += ', not checked\n'
    else:
        info += '\n'
    if link.redirectdepth > 0:
        if len(link.children) > 0:
            info += 'redirect: %s\n' % unicode(link.children[0].url, errors='replace')
        else:
            info += 'redirect (not followed)\n'
    if len(link.parents) == 1:
        info += 'linked from 1 page\n'
    elif len(link.parents) > 1:
        info += 'linked from %d pages\n' % len(link.parents)
    if link.mtime:
        info += 'last modified: %s\n' % time.ctime(link.mtime)
    if link.size:
        info += 'size: %s\n' % get_size(link.size)
    if link.mimetype:
        info += 'mime-type: %s\n' % unicode(link.mimetype, errors='replace')
    if link.encoding:
        info += 'encoding: %s\n' % unicode(link.encoding, errors='replace')
    for problem in link.linkproblems:
        info += 'problem: %s\n' % unicode(problem, errors='replace')
    # trim trailing newline
    return info.strip()

def make_link(link, title=None):
    """Return an <a>nchor to a url with title. If url is in the Linklist and
    is external, insert "class=external" in the <a> tag."""
    # try to fetch the link object for this url
    if link.isinternal:
        cssclass = 'internal'
    else:
        cssclass = 'external'
    if title is None:
        title = get_title(link)
    target = ''
    if config.REPORT_LINKS_IN_NEW_WINDOW:
        target = 'target="_blank" '
    # gather some information about the link to report
    return '<a href="'+htmlescape(link.url, True)+'" '+target+'class="'+cssclass+'" title="'+htmlescape(get_info(link), True)+'">'+htmlescape(title)+'</a>'

def print_parents(fp, link, indent='     '):
    """Write a list of parents to the output file descriptor.
    The output is indeted with the specified indent."""
    parents = link.parents
    # if there are no parents print nothing
    if len(parents) == 0:
        return
    parents.sort(lambda a, b: cmp(a.title, b.title) or cmp(a.url, b.url))
    fp.write(
      indent+'<div class="parents">\n'+
      indent+' referenced from:\n'+
      indent+' <ul>\n' )
    for parent in parents:
        fp.write(
          indent+'  <li>%(parent)s</li>\n'
          % { 'parent': make_link(parent) })
    fp.write(
      indent+' </ul>\n'+
      indent+'</div>\n' )

def open_file(filename, istext=True, makebackup=False):
    """This returns an open file object which can be used for writing. This
    file is created in the output directory. The output directory (stored in
    config.OUTPUT_DIR is created if it does not yet exist. If the second
    parameter is True (default) the file is opened as an UTF-8 text file."""
    import os
    # check if output directory exists and create it if needed
    if not os.path.isdir(config.OUTPUT_DIR):
        try:
            os.mkdir(config.OUTPUT_DIR)
        except OSError, (errno, strerror):
            debugio.error('error creating directory %(dir)s: %(strerror)s' %
                          { 'dir': config.OUTPUT_DIR,
                            'strerror': strerror })
            sys.exit(1)
    # build the output file name
    fname = os.path.join(config.OUTPUT_DIR, filename)
    # check if file exists
    if os.path.exists(fname):
        if makebackup:
            # create backup of original (overwriting previous backup)
            os.rename(fname, fname+'~')
        elif not config.OVERWRITE_FILES:
            # ask to overwrite
            res = raw_input('webcheck: overwrite %s? [y]es, [a]ll, [q]uit: ' % fname)
            res = res.lower() + ' '
            if res[0] == 'a':
                config.OVERWRITE_FILES = True
            elif res[0] != 'y':
                print 'Aborted.'
                sys.exit(1)
    # open the file for writing
    try:
        if istext:
            return open(fname, 'w')
        else:
            return open(fname, 'wb')
    except IOError, (errno, strerror):
        debugio.error('error creating output file %(fname)s: %(strerror)s' %
                      { 'fname': fname,
                        'strerror': strerror })
        sys.exit(1)

def _print_navbar(fp, plugin):
    """Return an html fragement representing the navigation bar for a page."""
    fp.write('  <ul class="navbar">\n')
    for p in config.PLUGINS:
        # import the plugin
        report = __import__('plugins.' + p, globals(), locals(), [p])
        # skip if no outputfile
        if not hasattr(report, '__outputfile__'):
            continue
        # generate a link to the plugin page
        selected = ''
        if report == plugin:
            selected = ' class="selected"'
        fp.write(
          '   <li><a href="%(pluginfile)s"%(selected)s title="%(description)s">%(title)s</a></li>\n'
          % { 'pluginfile' : report.__outputfile__,
              'selected'   : selected,
              'title'      : htmlescape(report.__title__),
              'description': htmlescape(report.__doc__) })
    fp.write('  </ul>\n')

def open_html(plugin, site):
    """Print an html fragment for the start of an html page."""
    # open the file
    fp = open_file(plugin.__outputfile__)
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
      '  <script language="javascript" type="text/javascript" src="fancytooltips.js"></script>\n'
      '  <meta name="Generator" content="webcheck %(version)s" />\n'
      ' </head>\n'
      ' <body>\n'
      '  <h1 class="basename">Webcheck report for <a href="%(siteurl)s">%(sitetitle)s</a></h1>\n'
      % { 'sitetitle':  htmlescape(get_title(site.linkMap[site.base])),
          'plugintitle': htmlescape(plugin.__title__),
          'siteurl':    site.base,
          'version':    config.VERSION })
    # write navigation bar
    _print_navbar(fp, plugin)
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
      % { 'time':     htmlescape(time.ctime(time.time())),
          'homepage': config.HOMEPAGE,
          'version':  htmlescape(config.VERSION) })
    fp.close()

def generate(site):
    """Generate pages for plugins."""
    for p in config.PLUGINS:
        debugio.info('  ' + p)
        # import the plugin
        plugin = __import__('plugins.' + p, globals(), locals(), [p])
        # run the plugin
        plugin.generate(site)
