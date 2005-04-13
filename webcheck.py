#!/usr/bin/env python

# webcheck.py - main module of webcheck doing command-line checking
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk) <marduk@python.net>
# Copyright (C) 2002 Mike Meyer <mwm@mired.org>
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


USAGE='webcheck [-abvqW][-l url][-x url]... [-y url]... [-r depth][-o dir][-w sec][-d level] url [location]...'
PYTHON_VERSION=1.5 # not used right now
explored = []
problem_db = {}
linkMap = {}

import sys
import time
import os


start_time = time.ctime(time.time())

# importing the config.py file is a real problem if the user did not install
# the files EXACTLY the way I said to... or even using the frozen version is
# becoming a real bitch.  I will just have to tell them right out how to fix it.
try:
    sys.path = ['.'] + sys.path
    import config
except ImportError:
    sys.stdout.write('Please verify that PYTHONPATH knows where to find "config.py"\n')
    sys.exit(1)

import myUrlLib
Link=myUrlLib.Link

# myUrlLib will be looking for a 'config' module.  set it up here.
myUrlLib.config=config

import debugio
debugio.DEBUG_LEVEL = config.DEBUG_LEVEL

import version

def parse_args():
    import getopt
    global URL
    try:
        optlist, args = getopt.getopt(sys.argv[1:],'vl:x:y:ar:o:bw:d:qW')
    except getopt.error, reason:
        print reason
        print USAGE
        sys.exit(1)
    for flag,arg in optlist:
        if flag=='-v':
            print_version()
            sys.exit(0)
        elif flag=='-x':
            config.EXCLUDED_URLS.append(arg)
        elif flag=='-y':
            config.YANKED_URLS.append(arg)
        elif flag=='-a':
            config.AVOID_EXTERNAL_LINKS=1
        elif flag=='-r':
            config.REDIRECT_DEPTH=int(arg)
        elif flag=='-o':
            config.OUTPUT_DIR=arg
        elif flag=='-b':
            config.BASE_URLS_ONLY=1
        elif flag=='-w':
            config.WAIT_BETWEEN_REQUESTS=int(arg)
        elif flag=='-l':
            config.LOGO_HREF=arg
        elif flag=='-W':
            config.OVERWRITE_FILES=1
        elif flag=='-d':
            debugio.DEBUG_LEVEL=int(arg)
        elif flag=='-q':
            debugio.DEBUG_LEVEL=0

    if len(args)==0:
        print USAGE
        sys.exit(1)
    else: URL = args[0]
    config.HOSTS = config.HOSTS + args[1:]

def print_version():
    """Print version information"""
    import os
    print "    Webcheck: " + version.webcheck
    print "    Python: " + sys.version
    print "    OS:     " + os.name
    print

def warn():
    """Warn the user that something has gone wrong."""
    print "*******************************************"
    print "*                                         *"
    print "* Warning, Webcheck has found nothing to  *"
    print "* report for this site.  If you feel this *"
    print "* is in error, please contact             *"
    print "* %s.                                     *" % version.author
    print "* and specify the environment that caused *"
    print "* this to occur.                          *"
    print "*                                         *"
    print "* Webcheck %s                             *" % version.webcheck
    print "*                                         *"
    print "*******************************************"

def link_image(filename):
    source = '/usr/share/webcheck/' + filename
    target = config.OUTPUT_DIR + filename
    if os.path.exists(target): return
    try:
       os.symlink(source, target)
    except os.error, (errcode, errtext):
       print 'Warning: "%s": %s' % (target, errtext)
       print '         Please copy "%s" to "%s".' % (source, target)

# set up the pages
plugins = config.PLUGINS

if __name__ == '__main__':

    parse_args()
    config.OUTPUT_DIR=config.OUTPUT_DIR + '/'

    debugio.write('checking site....')
    try:
        Link.base = Link(URL,None) # this will take a while
    except KeyboardInterrupt:
        sys.stderr.write("Interrupted\n")
        sys.exit(1)
    debugio.write('done.')
    if not hasattr(Link.base,"URL"):
        warn()
        sys.exit(1)

    linkMap = Link.linkMap

    # now we can write out the files
    # start with the frame-description page
    debugio.write('Generating reports...')
    from plugins.rptlib import main_index, nav_bar
    main_index()
    nav_bar(plugins)
    link_image('blackbar.png')
    if config.LOGO_HREF == 'webcheck.png': link_image('webcheck.png')
    debugio.write('done.')

