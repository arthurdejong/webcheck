#!/usr/bin/env python

# cmd.py - command-line front-end for webcheck
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike W. Meyer
# Copyright (C) 2005, 2006, 2007, 2008, 2010, 2011, 2013 Arthur de Jong
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

import argparse
import logging

import webcheck
import webcheck.monkeypatch
from webcheck.crawler import Crawler, default_cfg


version_string = '''
webcheck %s
Written by Albert Hopkins (marduk), Mike W. Meyer and Arthur de Jong.

Copyright (C) 1998-2013
Albert Hopkins (marduk), Mike W. Meyer and Arthur de Jong.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
'''.strip() % webcheck.__version__


class VersionAction(argparse.Action):

    def __init__(self, option_strings, dest,
                 help='output version information and exit'):
        super(VersionAction, self).__init__(
            option_strings=option_strings,
            dest=argparse.SUPPRESS,
            default=argparse.SUPPRESS,
            nargs=0,
            help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        print version_string
        parser.exit()


# set up command line parser
parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description='Generate a report for the given URLs.')
parser.add_argument(
    '-V', '--version', action=VersionAction)
parser.add_argument(
    '-i', '--internal', metavar='PATTERN', action='append',
    help='mark URLs matching PATTERN as internal')
parser.add_argument(
    '-x', '--external', metavar='PATTERN', action='append',
    help='mark URLs matching PATTERN as external')
parser.add_argument(
    '-y', '--yank', metavar='PATTERN', action='append',
    help='do not check URLs matching PATTERN')
parser.add_argument(
    '-b', '--base-only', action='store_true',
    help='base URLs only: consider any URL not starting with any of the base URLs to be external')
parser.add_argument(
    '-a', '--avoid-external', action='store_true',
    help='do not check external URLs')
parser.add_argument(
    '--ignore-robots', action='store_true',
    help='do not retrieve or parse robots.txt files')
parser.add_argument(
    '-q', '--quiet', '--silent', action='store_true',
    help='suppress progress messages')
parser.add_argument(
    '-d', '--debug', action='store_true',
    help='show programmer-level debug information')
parser.add_argument(
    '-o', '--output', dest='output_dir', metavar='DIRECTORY',
    help='store the generated reports in the specified directory')
parser.add_argument(
    '-c', '--continue', action='store_true',
    help='try to continue from a previous run')
parser.add_argument(
    '-f', '--force', action='store_true',
    help='overwrite files without asking')
parser.add_argument(
    '-r', '--redirects', metavar='N', type=int,
    help='the number of redirects webcheck should follow, 0 implies to follow all redirects')
parser.add_argument(
    '-l', '--max-depth', '--levels', metavar='N', type=int,
    help='maximum depth of links to follow from base urls')
parser.add_argument(
    '-w', '--wait', metavar='SECONDS', type=float,
    help='wait SECONDS between retrievals')
parser.add_argument(
    '--profile', action='store_true', help=argparse.SUPPRESS)
parser.add_argument(
    'base_urls', metavar='URL', nargs='+')
parser.set_defaults(**default_cfg)


def main(cfg):
    """Main program."""
    # configure logging
    if cfg.get('quiet', False):
        level = logging.WARNING
    elif cfg.get('debug', False):
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(format='webcheck: %(levelname)s: %(message)s', level=level)
    # set up crawler and go
    crawler = Crawler(cfg)
    logging.info('checking site....')
    crawler.crawl()
    logging.info('done.')
    logging.info('postprocessing....')
    crawler.postprocess()
    logging.info('done.')
    logging.info('generating reports...')
    crawler.generate()
    logging.info('done.')


def entry_point():
    """setuptools entry point"""
    args = parser.parse_args()
    main(vars(args))
