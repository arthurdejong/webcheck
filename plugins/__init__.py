
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

import sys
import urllib
import string
import debugio
import config
import time

def escape(txt, inattr=False):
    """HTML escape the given string and return an ASCII clean string with
    known entities and character entities for the other values."""
    import htmlentitydefs
    # the output string
    out = ''
    # convert to unicode object
    if type(txt) is str:
        txt = unicode(txt, errors='replace')
    # loop over the characters of the string
    for c in txt:
        if c == '"':
            if inattr:
                out += '&%s;' % htmlentitydefs.codepoint2name[ord(c)]
            else:
                out += '"'
        elif htmlentitydefs.codepoint2name.has_key(ord(c)):
            out += '&%s;' % htmlentitydefs.codepoint2name[ord(c)]
        elif ord(c) > 126:
            out += '&#%d;'% ord(c)
        elif inattr and c == u'\n':
            out += '&#10;'
        else:
            out += c.encode('utf-8')
    return out

def get_title(link):
    """Returns the title of a link if it is set otherwise returns url."""
    if link.title is None or link.title == '':
        return link.url
    return link.title

def _floatformat(f):
    """Return a float as a string while trying to keep it within three
    characters."""
    r = '%.1f' % f
    if len(r) > 3:
        r = r[:r.find('.')]
    return r

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

def make_link(link,title=None):
    """Return an <a>nchor to a url with title. If url is in the Linklist and
    is external, insert "class=external" in the <a> tag."""
    # try to fetch the link object for this url
    if link.isinternal:
        cssclass='internal'
    else:
        cssclass='external'
    if title is None:
        title=get_title(link)
    target=''
    if config.REPORT_LINKS_IN_NEW_WINDOW:
        target='target="_blank" '
    # gather some information about the link to report
    return '<a href="'+escape(link.url, True)+'" '+target+'class="'+cssclass+'" title="'+escape(get_info(link),True)+'">'+escape(title)+'</a>'

def print_parents(fp,link,indent='     '):
    # present a list of parents
    parents = link.parents
    # if there are no parents print nothing
    if len(parents) == 0:
        return
    parents.sort(lambda a, b: cmp(a.title, b.title))
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

def open_file(filename, istext=True):
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
    fname = os.path.join(config.OUTPUT_DIR,filename)
    # check if file exists and ask to overwrite
    if os.path.exists(fname) and not config.OVERWRITE_FILES:
        ow = raw_input('webcheck: overwrite %s? [y]es, [a]ll, [q]uit: ' % fname)
        ow = ow.lower() + " "
        if ow[0] == 'a':
            config.OVERWRITE_FILES = True
        elif ow[0] != 'y':
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

def print_navbar(fp, plugins, current):
    """Return a html fragement representing the navigation bar for a page."""
    fp.write('  <ul class="navbar">\n')
    for p in plugins:
        # if this is the first plugin, use index.html as filename
        filename = p + '.html'
        if p == plugins[0]:
            filename = 'index.html'
        # import the plugin
        report = __import__('plugins.' + p, globals(), locals(), [p])
        # generate a link to the plugin page
        selected = ''
        if p == current:
            selected = ' class="selected"'
        fp.write(
          '   <li><a href="%(pluginfile)s"%(selected)s title="%(description)s">%(title)s</a></li>\n'
          % { 'pluginfile' : filename,
              'selected'   : selected,
              'title'      : escape(report.__title__),
              'description': escape(report.__doc__) })
    fp.write('  </ul>\n')

def generate(site, plugins):
    """Generate pages for plugins."""
    for p in plugins:
        debugio.info('  ' + p)
        # if this is the first plugin, use index.html as filename
        filename = p + '.html'
        if p == plugins[0]:
            filename = 'index.html'
        report = __import__('plugins.' + p, globals(), locals(), [p])
        fp = open_file(filename)
        # write basic html head
        # TODO: make it possible to use multiple stylesheets (possibly reference external stylesheets)
        fp.write(
          '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
          '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n'
          '<html xmlns="http://www.w3.org/1999/xhtml">\n'
          ' <head>\n'
          '  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />\n'
          '  <title>Webcheck report for %(sitetitle)s</title>\n'
          '  <link rel="stylesheet" type="text/css" href="webcheck.css" />\n'
          '  <script language="javascript" type="text/javascript" src="fancytooltips.js"></script>\n'
          '  <meta name="Generator" content="webcheck %(version)s" />\n'
          ' </head>\n'
          ' <body>\n'
          '  <h1 class="basename">Webcheck report for <a href="%(siteurl)s">%(sitetitle)s</a></h1>\n'
          % { 'sitetitle':  escape(get_title(site.linkMap[site.base])),
              'siteurl':    site.base,
              'version':    config.VERSION })
        # write navigation bar
        print_navbar(fp, plugins, p)
        # write plugin heading
        fp.write('  <h2>%s</h2>\n' % escape(report.__title__))
        # write plugin contents
        fp.write('  <div class="content">\n')
        report.generate(fp,site)
        fp.write('  </div>\n')
        # write bottom of page
        fp.write(
          '  <p class="footer">\n'
          '   Generated %(time)s by <a href="%(homepage)s">webcheck %(version)s</a>\n'
          '  </p>\n'
          ' </body>\n'
          '</html>\n'
          % { 'time':     escape(time.ctime(time.time())),
              'homepage': config.HOMEPAGE,
              'version':  escape(config.VERSION) })
        fp.close()
