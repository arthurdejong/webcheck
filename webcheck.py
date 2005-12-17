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
#
# The files produced as output from the software do not automatically fall
# under the copyright of the software, unless explicitly stated otherwise.

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
    """Print the option list."""
    print \
        'Usage: webcheck [OPTION]... URL...\n' \
        'Generate a report for the given URLs\n' \
        '\n' \
        '  -x, --external=PATTERN mark URLs matching PATTERN as external\n' \
        '  -y, --yank=PATTERN     do not check URLs matching PATTERN\n' \
        '  -b, --base-only        base URLs only: consider any URL not starting with\n' \
        '                         the base URL to be external\n' \
        '  -a, --avoid-external   do not check external URLs\n' \
        '  -q, --quiet, --silent  suppress progress messages\n' \
        '  -d, --debug            do programmer-level debugging\n' \
        '  -o, --output=DIRECTORY store the generated reports in the specified\n' \
        '                         directory\n' \
        '  -f, --force            overwrite files without asking\n' \
        '  -r, --redirects=N      the number of redirects webcheck should follow,\n' \
        '                         0 implies to follow all redirects\n' \
        '  -w, --wait=SECONDS     wait SECONDS between retrievals\n' \
        '  -V, --version          output version information and exit\n' \
        '  -h, --help             display this help and exit' \

def parse_args(site):
    """Parse command-line arguments."""
    import getopt
    try:
        optlist, args = getopt.gnu_getopt(sys.argv[1:],
            'x:y:l:baqdo:fr:w:Vh',
            ('external=', 'yank=', 'base-only', 'avoid-external',
             'quiet', 'silent', 'debug', 'output=',
             'force', 'redirects=', 'wait=', 'version', 'help'))
    except getopt.error, reason:
        print >>sys.stderr,"webcheck: %s" % reason;
        print_tryhelp()
        sys.exit(1)
    for flag,arg in optlist:
        if flag in ('-x', '--external'):
            site.add_external_re(arg)
        elif flag in ('-y', '--yank'):
            site.add_yanked_re(arg)
        elif flag in ('-b', '--base-only'):
            config.BASE_URLS_ONLY = True
        elif flag in ('-a', '--avoid-external'):
            config.AVOID_EXTERNAL_LINKS = True
        elif flag in ('-q', '--quiet', '--silent'):
            debugio.loglevel = debugio.ERROR
        elif flag in ('-d', '--debug'):
            debugio.loglevel = debugio.DEBUG
        elif flag in ('-o', '--output'):
            config.OUTPUT_DIR = arg
        elif flag in ('-f', '--force'):
            config.OVERWRITE_FILES = True
        elif flag in ('-r', '--redirects'):
            config.REDIRECT_DEPTH = int(arg)
        elif flag in ('-w', '--wait'):
            config.WAIT_BETWEEN_REQUESTS = int(arg)
        elif flag in ('-V', '--version'):
            print_version()
            sys.exit(0)
        elif flag in ('-h', '--help'):
            print_help()
            sys.exit(0)
    if len(args)==0:
        print_usage()
        print_tryhelp()
        sys.exit(1)
    for arg in args:
        # if it does not look like a url it is probably a local file
        import urlparse
        import urllib
        if urlparse.urlsplit(arg)[0] == '':
            arg = 'file://' + urllib.pathname2url(os.path.abspath(arg))
        site.add_internal(arg)

def install_file(source, text=False):
    """Install the given file in the output directory.
    If the text flag is set to true it is assumed the file is text,
    translating line endings."""
    import shutil
    import urlparse
    # figure out mode to open the file with
    mode='r'
    if text:
        mode+='U'
    # check with what kind of argument we are called
    scheme = urlparse.urlsplit(source)[0]
    if scheme == 'file':
        # this is a file:/// url, translate to normal path and open
        source = urllib.url2pathname(urlparse.urlsplit(source)[2])
    elif scheme == '' and os.path.isabs(source):
        # this is an absolute path, just open it as is
        pass
    elif scheme == '':
        # this is a relavite path, try to fetch it from the python path
        for d in sys.path:
            tst = os.path.join(d,source)
            if os.path.isfile(tst):
                source = tst
                break
    # TODO: support more schemes here
    # figure out the destination name
    target = os.path.join(config.OUTPUT_DIR, os.path.basename(source))
    # test if source and target are the same
    source = os.path.realpath(source)
    if source == os.path.realpath(target):
        debugio.warn('attempt to overwrite %(fname)s with itself' % {'fname': source})
        return
    # open the input file
    sfp = None
    try:
        sfp = open(source, mode)
    except IOError, (errno, strerror):
        debugio.error('error opening %(fname)s: %(strerror)s' %
                      { 'fname': source,
                        'strerror': strerror })
        sys.exit(1)
    # create file in output directory (with overwrite question)
    tfp=plugins.open_file(os.path.basename(source));
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
