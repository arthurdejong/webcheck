#!/usr/bin/env python

# webcheck.py - main module of webcheck doing command-line checking
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
# Copyright (C) 2005 Arthur de Jong
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

import config
import crawler
import plugins
import debugio
import sys
import time
import os

debugio.loglevel=debugio.INFO

def print_version():
    """print version information"""
    print \
        "webcheck "+config.VERSION+"\n" \
        "Written by Albert Hopkins (marduk), Mike W. Meyer and Arthur de Jong.\n" \
        "\n" \
        "Copyright (C) 1998, 1999, 2002, 2005 Albert Hopkins (marduk), Mike W. Meyer\n" \
        "and Arthur de Jong.\n" \
        "This is free software; see the source for copying conditions.  There is NO\n" \
        "warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE."

def print_usage():
    """print short usage information"""
    print >>sys.stderr, \
        "Usage: webcheck [OPTION]... URL..."

def print_tryhelp():
    """print friendly pointer to more information"""
    print >>sys.stderr, \
        "Try `webcheck --help' for more information."

def print_help():
    """print option list"""
    print \
        "Usage: webcheck [OPTION]... URL...\n" \
        "Generate a report for the given URLs\n" \
        "\n" \
        "  -x PATTERN     mark URLs matching PATTERN as external\n" \
        "  -y PATTERN     do not check URLs matching PATTERN\n" \
        "  -b             base URLs only: consider any URL not starting with the base\n" \
        "                 URL to be external\n" \
        "  -a             do not check external URLs\n" \
        "  -q, --quiet, --silent\n" \
        "                 do not print out progress as webcheck traverses a site\n" \
        "  -d, --debug    set loglevel to LEVEL, for programmer-level debugging\n" \
        "  -o DIRECTORY   the directory in which webcheck will generate the reports\n" \
        "  -f, --force    overwrite files without asking\n" \
        "  -r N           the amount of redirects webcheck should follow when following\n" \
        "                 a link, 0 implies follow all redirects.\n" \
        "  -w, --wait=SECONDS\n" \
        "                 wait SECONDS between retrievals\n" \
        "  -V, --version  output version information and exit\n" \
        "  -h, --help     display this help and exit"

def parse_args(site):
    """parse command-line arguments"""
    import getopt
    try:
        optlist, args = getopt.gnu_getopt(sys.argv[1:],
            "x:y:l:baqdo:fr:w:Vh",
            ["quiet","silent","debug","force","wait=","version","help"])
    except getopt.error, reason:
        print >>sys.stderr,"webcheck: %s" % reason;
        print_tryhelp()
        sys.exit(1)
    for flag,arg in optlist:
        if flag=='-x':
            site.add_external_re(arg)
        elif flag=='-y':
            site.add_yanked_re(arg)
        elif flag=='-b':
            config.BASE_URLS_ONLY = True
        elif flag=='-a':
            config.AVOID_EXTERNAL_LINKS = True
        elif flag in ("-q","--quiet","--silent"):
            debugio.loglevel = debugio.ERROR
        elif flag in("-d","--debug"):
            debugio.loglevel = debugio.DEBUG
        elif flag=='-o':
            config.OUTPUT_DIR = arg
        elif flag in ("-f","--force"):
            config.OVERWRITE_FILES = True
        elif flag=='-r':
            config.REDIRECT_DEPTH = int(arg)
        elif flag in ("-w","--wait"):
            config.WAIT_BETWEEN_REQUESTS = int(arg)
        elif flag in ("-V","--version"):
            print_version()
            sys.exit(0)
        elif flag in ("-h","--help"):
            print_help()
            sys.exit(0)
    if len(args)==0:
        print_usage()
        print_tryhelp()
        sys.exit(1)
    for arg in args:
        site.add_internal(arg)

def find_file(fname):
    """Search the python path for the file name and return full path of the
    file."""
    for dname in sys.path:
        res = os.path.join(dname,fname)
        if os.path.isfile(res):
            return res
    return None

def install_file(fname,text=False):
    """Install the given file in the output directory.
    If the text flag is set to true it is assumed the file is text,
    translating line endings."""
    import shutil
    # TODO: extend so that if
    #  - filename has no slashes in it: search python path
    #  - filename starts with a known scheme: use that
    #  - filename starts with slash: treat is as a file://///// url
    # TODO: make it possible to reference the original location instead of copying the file
    # FIXME: check that source and target are different before opening file for writing
    source = find_file(fname)
    target = os.path.basename(fname)
    # open the input file, TODO: use the scheme stuff for doing this
    mode='r'
    if text:
        mode+='U'
    sfp=open(source,mode)
    # create file in output directory (with overwrite question)
    tfp=plugins.open_file(target);
    # copy contents
    shutil.copyfileobj(sfp,tfp)
    # close files
    tfp.close()
    sfp.close()

def main():
    site = crawler.Site()
    # parse command-line arguments
    parse_args(site)
    # crawl through the website
    debugio.info('checking site....')
    try:
        site.crawl() # this will take a while
    except KeyboardInterrupt:
        sys.stderr.write("Interrupted\n")
        sys.exit(1)
    debugio.info('done.')
    # now we can write out the files
    # start with the frame-description page
    debugio.info('generating reports...')
    # for every plugin, generate a page
    plugins.generate(site, config.PLUGINS)
    # put extra files in the output directory
    install_file('webcheck.css',True)
    debugio.info('done.')

if __name__ == '__main__':
    main()
