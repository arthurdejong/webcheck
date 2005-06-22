
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
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA

__version__ = '1.0'
__author__ = 'mwm@mired.org'

import sys
import urllib
import string
import debugio
import version
import config

problem_db = {}

# get the stylesheet for insertion,
# Note that I do it this way for two reasons.  One is that Netscape reportedly
# handles stylesheets better when they are inlined.  Two is that people often
# forget to put webcheck.css in the output directory.
if config.PROXIES is None:
    config.PROXIES = urllib.getproxies()
opener = urllib.FancyURLopener(config.PROXIES)
opener.addheaders = [('User-agent','Webcheck ' + version.webcheck)]
try:
    stylesheet =  opener.open(config.STYLESHEET).read()
except:
    stylesheet = ''

def get_title(link):
    """Returns the title of a link if it is set otherwise returns url."""
    if link.title is None:
        return url
    return link.title

def make_link(url,title=None):
    """Return an <a>nchor to a url with title. If url is in the Linklist and
    is external, insert "class=external" in the <a> tag."""
    # try to fetch the link object for this url
    cssclass='internal'
    try:
        global mySite
        link=mySite.linkMap[url]
        if link.external:
            cssclass='external'
        if title is None:
            title=link.title
    except KeyError:
        pass
    if title is None or title == "":
        title=url
    return '<a href="'+url+'" class="'+cssclass+'">'+title+'</a>'

def add_problem(type,link):
    """ Add a problem link to the 'problems' database.  Will not add external links """
    if link.external:
        return
    global problem_db
    author = link.author
    if problem_db.has_key(author):
        problem_db[author].append((type,link))
    else:
        problem_db[author]=[(type,link)]

def sort_by_age(a,b):
    """ Sort helper for url's age.  a and b are urls in linkMap """
    global mySite
    aage, bage = mySite.linkMap[a].age, mySite.linkMap[b].age
    if aage < bage:
        return -1
    elif aage == bage:
        return sort_by_author(a,b)
    else:
        return 1

def sort_by_rev_age(a,b):
    global mySite
    aage, bage = mySite.linkMap[a].age, mySite.linkMap[b].age
    if aage > bage:
        return -1
    elif aage == bage:
        return sort_by_author(a,b)
    else:
        return 1

def sort_by_author(a,b):
    global mySite
    aauthor,bauthor = mySite.linkMap[a].author, mySite.linkMap[b].author
    if aauthor < bauthor:
        return -1
    elif aauthor == bauthor:
        return 0
    else:
        return 1

def sort_by_size(a,b):
    global mySite
    asize, bsize = mySite.linkMap[a].totalSize, mySite.linkMap[b].totalSize
    if asize > bsize:
        return -1
    elif asize == bsize:
        return 0
    else:
        return 1

def open_file(filename):
    """ given config.OUTPUT_DIR checks if the directory already exists; if not, it creates it, and then opens
    filename for writing and returns the file object """
    import os
    if os.path.isdir(config.OUTPUT_DIR) == 0:
        os.mkdir(config.OUTPUT_DIR)
    fname = config.OUTPUT_DIR + filename
    if os.path.exists(fname) and not config.OVERWRITE_FILES:
        # mv: overwrite `/tmp/b'?
        # cp: overwrite `/tmp/b'?
        ow = raw_input('File %s already exists. Overwrite? y[es]/a[ll]/Q[uit] ' % fname)
        ow = ow.lower() + " "
        if ow[0] == 'a':
            config.OVERWRITE_FILES = 1
        elif ow[0] != 'y':
            print 'Aborted.'
            sys.exit(0)
    return open(fname,'w')

def main_index(fname, site):
    """ Write out the frameset. """
    # FIXME: get rid of this once we have a better way of passing this information
    global mySite
    mySite=site
    fp = open_file(fname)
    fp.write('<html>\n')
    fp.write('<head>\n')
    fp.write('<title>Webcheck report for "%s"</title>\n' % get_title(site.linkMap[site.base]))
    fp.write('<style type="text/css">\n')
    fp.write('<!-- /* hide from old browsers */\n')
    fp.write(stylesheet+'\n')
    fp.write(' --> </style>\n')
    fp.write('</head>\n')
    fp.write('<frameset COLS="%s,*" border=0 framespacing=0>\n' % config.NAVBAR_WIDTH)
    fp.write('<frame name="navbar" src="%s" marginwidth=0 marginheight=0 frameborder=0>\n' \
             % config.NAVBAR_FILENAME)
    fp.write('<frame name="main" src="%s" frameborder=0>\n' % (config.PLUGINS[0]+'.html'))
    fp.write('</frameset>\n')
    fp.write('</html>\n')
    fp.close()

def nav_bar(fname, site, plugins):
    """ Write out the navigation bar frame. """
    fp=open_file(fname)
    # print page header
    fp.write('<html>\n')
    fp.write('<head>\n')
    fp.write('<title>navbar</title>\n')
    fp.write('<style type="text/css">\n')
    fp.write('<!-- /* hide from old browsers */\n')
    fp.write(stylesheet+'\n')
    fp.write(' --> </style>\n')
    fp.write('<base target="main">\n')
    fp.write('</head>\n')
    fp.write('<body class="navbar">\n')
    fp.write('<div align="center">\n')
    fp.write('<table cellpadding="%s" cellspacing="%s">\n' \
             % (config.NAVBAR_PADDING, config.NAVBAR_SPACING))
    # webcheck title with link to homepage
    fp.write('<tr><th class="home">\n')
    fp.write('<a target="_top" href="%s" onMouseOver="window.status=\'Webcheck Home Page\'; return true;">Webcheck %s</a></th></tr>\n' \
             % (version.home, version.webcheck))
    # labels pointing to each individual page
    for plugin in plugins:
        filename = plugin + '.html'
        fp.write('<tr><th>\n')
        report = __import__('plugins.' + plugin, globals(), locals(), [plugin])
        fp.write('<strong><a href="%s" onMouseOver="window.status=\'%s\'; return true">%s</a></strong>\n' \
              % (filename, report.__doc__, report.__title__))
        fp.write('</th></tr>\n')
    # print the page footer
    fp.write('</table>\n')
    fp.write('</div>\n')
    fp.write('</body>\n')
    fp.write('</html>\n')
    # close file
    fp.close()

def gen_plugins(site,plugins):
    """ Generate pages for plugins. """
    for plugin in plugins:
        debugio.info('  ' + plugin)
        filename = plugin + '.html'
        report = __import__('plugins.' + plugin, globals(), locals(), [plugin])
        fp = open_file(filename)
        doTopMain(fp,site,report)
        report.generate(fp,site)
        doBotMain(fp)
        fp.close()

def doTopMain(fp,site,report):
    """ Write top part of html file for main content frame. """
    fp.write('<html>\n')
    fp.write('<head><title>%s</title>\n' % report.__title__)
    fp.write('<style type="text/css">\n')
    fp.write('<!-- /* hide from old browsers */\n')
    fp.write(stylesheet+'\n')
    fp.write(' --> </style>\n')
    fp.write('<meta name="Generator" content="Webcheck ' + version.webcheck + '">\n')
    fp.write('</head>\n')
    fp.write('<body class="%s">\n' % string.split(report.__name__,'.')[1])
    fp.write('<p class="logo"><a href="%s"><img src="%s" border="0" alt=""></a></p>\n' % (site.base, config.LOGO_HREF))
    fp.write('<h1 class="basename">%s</h1>\n' % make_link(site.base))
    fp.write('</h1>\n')
    fp.write('\n\n<table width="100%" cellpadding="4">\n')
    fp.write('  <tr><th class="title">%s</th></tr>\n</table>\n' % report.__title__)

def doBotMain(fp):
    """ Write bottom part of html file for main content frame. """
    import webcheck
    fp.write('<hr>\n');
    fp.write('<p class="footer">\n')
    fp.write('<em>Generated %s by <a target="_top" href="%s">Webcheck %s</a></em></p>\n' % (webcheck.start_time,version.home, version.webcheck))
    fp.write('</body>\n')
    fp.write('</html>\n')
