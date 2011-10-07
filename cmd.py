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

import os
import re
import sys
import urllib
import urlparse

import webcheck
from webcheck import config
from webcheck import debugio
import webcheck.crawler
import webcheck.db
import webcheck.monkeypatch
import webcheck.plugins

debugio.loglevel = debugio.INFO

# Whether to produce profiling information. This is for development
# purposes and as such undocumented.
# http://docs.python.org/lib/profile.html
PROFILE = False


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
      '  -w, --wait=SECONDS     wait SECONDS between retrievals\n'
      '  -V, --version          output version information and exit\n'
      '  -h, --help             display this help and exit\n'
      % {'redirects': config.REDIRECT_DEPTH})


def parse_args(site):
    """Parse command-line arguments."""
    import getopt
    try:
        optlist, args = getopt.gnu_getopt(sys.argv[1:],
          'i:x:y:l:baqdo:cfr:u:w:Vh',
          ('internal=', 'external=', 'yank=', 'base-only', 'avoid-external',
           'ignore-robots',
           'quiet', 'silent', 'debug', 'profile', 'output=', 'continue',
           'force', 'redirects=', 'wait=', 'version', 'help'))
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
                debugio.loglevel = debugio.ERROR
            elif flag in ('-d', '--debug'):
                debugio.loglevel = debugio.DEBUG
            elif flag in ('--profile',):
                # undocumented on purpose
                global PROFILE
                PROFILE = True
            elif flag in ('-o', '--output'):
                config.OUTPUT_DIR = arg
            elif flag in ('-c', '--continue'):
                config.CONTINUE = True
            elif flag in ('-f', '--force'):
                config.OVERWRITE_FILES = True
            elif flag in ('-r', '--redirects'):
                config.REDIRECT_DEPTH = int(arg)
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
        # ensure output directory exists
        if not os.path.isdir(config.OUTPUT_DIR):
            os.mkdir(config.OUTPUT_DIR)
        # set up database connection
        filename = os.path.join(config.OUTPUT_DIR, 'webcheck.sqlite')
        from sqlalchemy import create_engine
        engine = create_engine('sqlite:///' + filename)
        webcheck.db.Session.configure(bind=engine)
        # ensure that all tables are created
        webcheck.db.Base.metadata.create_all(engine)
        # TODO: schema migraton goes here
        # add configuration to site
        for pattern in internal_urls:
            site.add_internal_re(pattern)
        for pattern in external_urls:
            site.add_external_re(pattern)
        for pattern in yank_urls:
            site.add_yanked_re(pattern)
        for arg in args:
            # if it does not look like a url it is probably a local file
            if urlparse.urlsplit(arg)[0] == '':
                arg = 'file://' + urllib.pathname2url(os.path.abspath(arg))
            site.add_internal(arg)
    except getopt.error, reason:
        sys.stderr.write('webcheck: %s\n' % reason)
        print_tryhelp()
        sys.exit(1)
    except re.error, e:
        sys.stderr.write('webcheck: %s\n' % str(e))
        sys.exit(1)


def install_file(source, text=False):
    """Install the given file in the output directory.
    If the text flag is set to true it is assumed the file is text,
    translating line endings."""
    import shutil
    import urlparse
    # figure out mode to open the file with
    mode = 'r'
    if text:
        mode += 'U'
    # check with what kind of argument we are called
    scheme = urlparse.urlsplit(source)[0]
    if scheme == 'file':
        # this is a file:/// url, translate to normal path and open
        import urllib
        source = urllib.url2pathname(urlparse.urlsplit(source)[2])
    elif scheme == '' and os.path.isabs(source):
        # this is an absolute path, just open it as is
        pass
    elif scheme == '':
        # this is a relavite path, try to fetch it from the python path
        for directory in sys.path:
            tst = os.path.join(directory, source)
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
        debugio.error('%(fname)s: %(strerror)s' %
                      {'fname': source,
                       'strerror': strerror})
        sys.exit(1)
    # create file in output directory (with overwrite question)
    tfp = webcheck.plugins.open_file(os.path.basename(source))
    # copy contents
    shutil.copyfileobj(sfp, tfp)
    # close files
    tfp.close()
    sfp.close()


def main(site):
    """Main program."""
    # crawl through the website
    debugio.info('checking site....')
    webcheck.crawler.setup_urllib2()
    site.crawl()  # this will take a while
    debugio.info('done.')
    # do postprocessing (building site structure, etc)
    debugio.info('postprocessing....')
    site.postprocess()
    debugio.info('done.')
    # now we can write out the files
    # start with the frame-description page
    debugio.info('generating reports...')
    # for every plugin, generate a page
    site.generate()
    # put extra files in the output directory
    install_file('webcheck.css', True)
    install_file('fancytooltips/fancytooltips.js', True)
    install_file('favicon.ico', False)
    debugio.info('done.')


if __name__ == '__main__':
    try:
        # initialize site object
        site = webcheck.crawler.Site()
        # parse command-line arguments
        parse_args(site)
        # run the main program
        if PROFILE:
            fname = os.path.join(config.OUTPUT_DIR, 'webcheck.prof')
            try:
                import cProfile
            except ImportError:
                import profile as cProfile
            try:
                import sqltap
                sqltap.start()
            except ImportError:
                pass
            cProfile.run('main(site)', fname)
            if 'sqltap' in locals():
                statistics = sqltap.collect()
                sqltap.report(statistics, os.path.join(config.OUTPUT_DIR, 'sqltap.html'))
        else:
            main(site)
    except KeyboardInterrupt:
        sys.stderr.write('Interrupted\n')
        sys.exit(1)
