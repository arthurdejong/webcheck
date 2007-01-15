
# config.py - configuration state for webcheck
#
# Copyright (C) 1998, 1999 Albert Hopkins (marduk)
# Copyright (C) 2002 Mike Meyer
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

"""Configuration state for webcheck.

This file contains the default configuration for webcheck. All configurable
items should be changeble from the command line."""

import urllib

# Current version of webcheck.
VERSION = '1.9.8'

# The homepage of webcheck.
HOMEPAGE = 'http://ch.tudelft.nl/~arthur/webcheck/'

# Whether to consider any URL not starting with the base URL to be external.
# This is the state of the -b command line option.
BASE_URLS_ONLY = False

# Avoid checking external links at all. This is the state of the -a command
# line option.
AVOID_EXTERNAL_LINKS = False

# The proxy configuration.
PROXIES = urllib.getproxies_environment()

# IO timeout as passed to socket.setdefaulttimeout()
# value is a float in seconds None disables the timeout
IOTIMEOUT = 10.0

# Output directory. This is the state of the -o command line option.
OUTPUT_DIR = '.'

# Whether to try to read a state file to continue from.
CONTINUE = False

# This is the time in seconds to wait between requests. This is the state of
# the -w command line option.
WAIT_BETWEEN_REQUESTS = 0

# Redirect depth, the number of redirects to follow. This is the state of the
# -r command line option.
REDIRECT_DEPTH = 5

# The list of plugins that will be used to generate the report.
PLUGINS = [ 'anchors',
            'sitemap',
            'urllist',
            'images',
            'external',
            'notchkd',
            'badlinks',
            'old',
            'new',
            'size',
            'notitles',
            'problems',
            'about' ]

# Whether to overwrite files without asking. This is the state of the -f
# command line option.
OVERWRITE_FILES = False

# Whether to add extra headers to outgoing requests, requesting to
# disable caching, ensuring that a fresh page is returned
BYPASSHTTPCACHE = False

# The number of levels the sitemap plugin should show.
REPORT_SITEMAP_LEVEL = 8

# The age of pages in days that after which a page is considered too old.
REPORT_WHATSOLD_URL_AGE = 700

# The age of pages in days within wich a page is considered new.
REPORT_WHATSNEW_URL_AGE = 7

# The size of a page in kilobytes after which the page is considered too big.
REPORT_SLOW_URL_SIZE = 76

# Whether to open links in a new window (add target="_blank")
# (disabled by default because it is not xhtml 1.1)
REPORT_LINKS_IN_NEW_WINDOW = False

# A list of names that will be checked when encountering an file:///
# directory. This file will be picked up instead of the directory list.
FILE_INDEXES = [ 'index.html', 'index.htm' ]

# A list of names that will be checked when encountering an ftp://
# directory. This file will be picked up instead of the directory list.
FTP_INDEXES = [ 'index.html', 'index.htm' ]

# Whether to fetch robots.txt files and do checking based on the information
# present in those files (normally matching links are yanked).
USE_ROBOTS = False
