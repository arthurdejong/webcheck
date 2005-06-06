
# rptlib.py - plugin function module
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

__version__ = '1.0'
__author__ = 'mwm@mired.org'

import sys
import webcheck
import urllib
import string
import os
import debugio
import version

Link = webcheck.Link
linkMap = Link.linkMap
config = webcheck.config
proxies = config.PROXIES

problem_db = {}

# get the stylesheet for insertion,
# Note that I do it this way for two reasons.  One is that Netscape reportedly
# handles stylesheets better when they are inlined.  Two is that people often
# forget to put webcheck.css in the output directory.
if proxies is None:
    proxies = urllib.getproxies()
opener = urllib.FancyURLopener(proxies)
opener.addheaders = [('User-agent','Webcheck ' + version.webcheck)]
try:
    stylesheet =  opener.open(config.STYLESHEET).read()
except:
    stylesheet = ''

def get_title(url):
    """ returns the title of a url if it is not None, else returns url
    note that this implies linkMap[url] """
    link=linkMap[url]
    if link.title is None:
        return url
    return link.title

def make_link(url,text):
    """Return an <A>nchor to a url with <text>.  If url is in the Linklist and
    is external, insert "class=external" in the <A> tag."""
    url = str(url) # because sometimes I lazily pass a Link object.
    mystring = '<a href="' + url + '"'
    try:
        external = linkMap[url].external
    except KeyError:
        external = 0
    if external:
        mystring = mystring + ' class="external"'
    else:
        mystring = mystring + ' class="internal"'
    mystring = mystring + '>' + text + '</a>'
    return mystring

def add_problem(type,link):
    """ add a problem to the 'problems' database.  Will not add external links"""
    if link.external: return
    global problem_db
    author = link.author
    if problem_db.has_key(author):
        problem_db[author].append((type,link))
    else:
        problem_db[author]=[(type,link)]

def sort_by_age(a,b):
    """ sort helper for url's age.  a and b are urls in linkMap """
    aage, bage = linkMap[a].age, linkMap[b].age
    if aage < bage:
        return -1
    if aage == bage:
        return sort_by_author(a,b)
    return 1

def sort_by_rev_age(a,b):
    aage, bage = linkMap[a].age, linkMap[b].age
    if aage > bage:
        return -1
    if aage == bage:
        return sort_by_author(a,b)
    return 1

def sort_by_author(a,b):
    aauthor,bauthor = `linkMap[a].author`, `linkMap[b].author`
    if aauthor < bauthor:
        return -1
    if aauthor == bauthor:
        return 0
    return 1

def sort_by_size(a,b):
    asize, bsize = linkMap[a].totalSize, linkMap[b].totalSize
    if asize < bsize:
        return 1
    if asize == bsize:
        return 0
    return -1

def main_index():
    tmp = sys.stdout
    fp = open_file(config.MAIN_FILENAME)
    sys.stdout=fp
    
    print '<html>'
    print '<head>'
    print '<title>Webcheck report for "%s"</title>' % get_title(`Link.base`)
    print '<style type="text/css">'
    print '<!-- /* hide from old browsers */'
    print stylesheet
    print ' --> </style>'
    print '</head>'
    print '<frameset COLS="%s,*" border=0 framespacing=0>' \
          % config.NAVBAR_WIDTH
    print '<frame name="navbar" src="%s" marginwidth=0 marginheight=0 frameborder=0>' \
          % config.NAVBAR_FILENAME
    print '<frame name="main" src="%s" frameborder=0>' % (webcheck.plugins[0]+'.html')
    print '</frameset>'
    print '</html>'
    fp.close()
    sys.stdout = tmp


def nav_bar(plugins):
    # navigation bar
    fp=open_file(config.NAVBAR_FILENAME)
    stdout = sys.stdout
    sys.stdout = fp
    print '<html>\n<head>'
    print '  <title>navbar</title>'
    print '<style type="text/css">'
    print '<!-- /* hide from old browsers */'
    print stylesheet
    print ' --> </style>'
    print '  <base target="main">'
    print '</head>'
    print '<body class="navbar">'
    print '<div align=center>'
    print '<table cellpadding="%s" cellspacing="%s">' \
          % (config.NAVBAR_PADDING, config.NAVBAR_SPACING)
    # title
    print '<tr><th class="home">',
    print '<a target="_top" href="%s" onMouseOver="window.status=\'Webcheck Home Page\'; return true;">Webcheck %s</a></th></tr>' \
          % (version.home, version.webcheck)

    # labels pointing to each individual page
    for plugin in plugins + ['problems']:
        debugio.info('  ' + plugin)
        filename = plugin + '.html'
        print '<tr><th>',
        report = __import__('plugins.' + plugin, globals(), locals(), [plugin])
        print '<strong><a href="%s" onMouseOver="window.status=\'%s\'; return true">%s</a></strong>' \
              % (filename, report.__doc__, report.title),
        print '</th></tr>'

        # create the file we just pointed to
        tmp = sys.stdout
        fp = open_file(filename)
        sys.stdout = fp
        doTopMain(report)
        report.generate()
        report_version = report.__version__
        doBotMain()
        fp.close()
        sys.stdout = tmp
    
    print
    print '</table>'
    print '</div>'
    print '</body>'
    print '</html>'

    fp.close()
    sys.stdout = stdout

def open_file(filename):
    """ given config.OUTPUT_DIR checks if the directory already exists; if not, it creates it, and then opens         filename for writing and returns the file object """
    if os.path.isdir (config.OUTPUT_DIR) == 0:
        os.mkdir(config.OUTPUT_DIR)

    fname = config.OUTPUT_DIR + filename
    tmp = sys.stdout
    sys.stdout = sys.__stdout__
    if os.path.exists(fname) and not config.OVERWRITE_FILES:
        ow = raw_input('File %s already exists. Overwrite? y[es]/a[ll]/Q[uit] ' % `fname`)
        ow = ow.lower() + " "
        if ow[0] == 'a':
            config.OVERWRITE_FILES = 1
        elif ow[0] != 'y':
            print 'Aborted.'
            sys.exit(0)
    sys.stdout = tmp
    return open(fname,'w')

def doTopMain(report):
    """top part of html files in main frame prints to stdout"""
    print '<html>'
    print '<head><title>%s</title>' % report.title
    print '<style type="text/css">'
    print '<!-- /* hide from old browsers */'
    print stylesheet
    print ' --> </style>'
    print '<meta name="Author" content="Webcheck ' + version.webcheck + '">' 
    print '</head>'
    print '<body class="%s">' % string.split(report.__name__,'.')[1]  
    print '<p class="logo"><a '
    print 'href="%s"><img src="%s" border=0 alt=""></a></p>' % (Link.base, config.LOGO_HREF)
    print '\n<h1 class="basename">'
    print '  <a href="%s">%s</a>' \
          % (`Link.base`, get_title(`Link.base`))
    print '</h1>'
    print '\n\n<table width="100%" cellpadding=4>'
    print '  <tr><th class="title">%s</th></tr>\n</table>\n' % report.title

def doBotMain():
    """ bottom part of html files in main frame"""
    print 
    print '<hr>'
    print '<p class="footer">'
    print '<em>Generated %s by <a target="_top" href="%s">Webcheck %s</a></em></p>' \
          % (webcheck.start_time,version.home, version.webcheck)
    print '</body>'
    print '</html>'
