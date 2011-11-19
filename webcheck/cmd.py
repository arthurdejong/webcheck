#!/usr/bin/env python

# cmd.py - command-line front-end for webcheck
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
# Copyright (C) 2005, 2006, 2007, 2008, 2010, 2011 Arthur de Jong
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

"""This is the main webcheck module."""

import getopt
import logging
import os
import re
import sys
import urllib
import urlparse

import webcheck
import webcheck.monkeypatch
from webcheck import config
from webcheck.crawler import Crawler

# The loglevel to use for the logger that is configured.
LOGLEVEL = logging.INFO


def print_version():
    """Print version information."""
    sys.stdout.write(
      'webcheck %(version)s\n'
      'Written by Albert Hopkins (marduk), Mike W. Meyer and Arthur de Jong.\n'
      '\n'
      'Copyright (C) 1998-2011\n'
      'Albert Hopkins (marduk), Mike W. Meyer and Arthur de Jong.\n'
      'This is free software; see the source for copying conditions.  There is NO\n'
      'warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.\n'
      % {'version': webcheck.__version__})


def print_usage():
    """Print short usage information."""
    sys.stderr.write(
      'Usage: webcheck [OPTION]... URL...\n')


def print_tryhelp():
    """Print friendly pointer to more information."""
    sys.stderr.write(
      'Try \'webcheck --help\' for more information.\n')


def print_help():
    """Print the option list."""
    sys.stdout.write(
      'Usage: webcheck [OPTION]... URL...\n'
      'Generate a report for the given URLs\n'
      '\n'
      '  -i, --internal=PATTERN mark URLs matching PATTERN as internal\n'
      '  -x, --external=PATTERN mark URLs matching PATTERN as external\n'
      '  -y, --yank=PATTERN     do not check URLs matching PATTERN\n'
      '  -b, --base-only        base URLs only: consider any URL not starting\n'
      '                         with any of the base URLs to be external\n'
      '  -a, --avoid-external   do not check external URLs\n'
      '      --ignore-robots    do not retrieve and parse robots.txt files\n'
      '  -q, --quiet, --silent  suppress progress messages\n'
      '  -d, --debug            do programmer-level debugging\n'
      '  -o, --output=DIRECTORY store the generated reports in the specified\n'
      '                         directory\n'
      '  -c, --continue         try to continue from a previous run\n'
      '  -f, --force            overwrite files without asking\n'
      '  -r, --redirects=N      the number of redirects webcheck should follow,\n'
      '                         0 implies to follow all redirects (default=%(redirects)d)\n'
      '  -l, --levels=N         maximum depth of links to follow from base urls (default=inf)\n'
      '  -w, --wait=SECONDS     wait SECONDS between retrievals\n'
      '  -V, --version          output version information and exit\n'
      '  -h, --help             display this help and exit\n'
      % {'redirects': config.REDIRECT_DEPTH})

def parse_args(crawler):
    """Parse command-line arguments."""
    # these global options are set here
    global LOGLEVEL
    try:
        optlist, args = getopt.gnu_getopt(sys.argv[1:],
          'i:x:y:l:baqdo:cfr:u:w:Vh',
          ('internal=', 'external=', 'yank=', 'base-only', 'avoid-external',
           'ignore-robots',
           'quiet', 'silent', 'debug', 'profile', 'output=', 'continue',
           'force', 'redirects=', 'levels=', 'wait=', 'version', 'help'))
        internal_urls = []
        external_urls = []
        yank_urls = []
        for flag, arg in optlist:
            if flag in ('-i', '--internal'):
                internal_urls.append(arg)
            elif flag in ('-x', '--external'):
                external_urls.append(arg)
            elif flag in ('-y', '--yank'):
                yank_urls.append(arg)
            elif flag in ('-b', '--base-only'):
                config.BASE_URLS_ONLY = True
            elif flag in ('-a', '--avoid-external'):
                config.AVOID_EXTERNAL_LINKS = True
            elif flag in ('--ignore-robots',):
                config.USE_ROBOTS = False
            elif flag in ('-q', '--quiet', '--silent'):
                LOGLEVEL = logging.WARNING
            elif flag in ('-d', '--debug'):
                LOGLEVEL = logging.DEBUG
            elif flag in ('--profile',):
                # undocumented on purpose
                pass
            elif flag in ('-o', '--output'):
                config.OUTPUT_DIR = arg
            elif flag in ('-c', '--continue'):
                config.CONTINUE = True
            elif flag in ('-f', '--force'):
                config.OVERWRITE_FILES = True
            elif flag in ('-r', '--redirects'):
                config.REDIRECT_DEPTH = int(arg)
            elif flag in ('-l', '--levels'):
                config.MAX_DEPTH = int(arg)
            elif flag in ('-w', '--wait'):
                config.WAIT_BETWEEN_REQUESTS = float(arg)
            elif flag in ('-V', '--version'):
                print_version()
                sys.exit(0)
            elif flag in ('-h', '--help'):
                print_help()
                sys.exit(0)
        if len(args) == 0 and not config.CONTINUE:
            print_usage()
            print_tryhelp()
            sys.exit(1)
        # add configuration to site
        for pattern in internal_urls:
            crawler.add_internal_re(pattern)
        for pattern in external_urls:
            crawler.add_external_re(pattern)
        for pattern in yank_urls:
            crawler.add_yanked_re(pattern)
        for arg in args:
            # if it does not look like a url it is probably a local file
            if urlparse.urlsplit(arg)[0] == '':
                arg = 'file://' + urllib.pathname2url(os.path.abspath(arg))
            crawler.add_base(arg)
    except getopt.error, reason:
        sys.stderr.write('webcheck: %s\n' % reason)
        print_tryhelp()
        sys.exit(1)
    except re.error, e:
        sys.stderr.write('webcheck: %s\n' % str(e))
        sys.exit(1)


def main(crawler):
    """Main program."""
    # configure logging
    logging.basicConfig(format='webcheck: %(levelname)s: %(message)s', level=LOGLEVEL)
    # crawl through the website
    logging.info('checking site....')
    crawler.crawl()  # this will take a while
    logging.info('done.')
    # do postprocessing (building site structure, etc)
    logging.info('postprocessing....')
    crawler.postprocess()
    logging.info('done.')
    # now we can write out the files
    # start with the frame-description page
    logging.info('generating reports...')
    # for every plugin, generate a page
    crawler.generate()
    logging.info('done.')

def entry_point():
    """setuptools entry point"""
    # initialize crawler object
    crawler = Crawler()
    # parse command-line arguments
    parse_args(crawler)
    # run the main program
    main(crawler)
