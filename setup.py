#!/usr/bin/env python

# setup.py - webcheck installation script
#
# Copyright (C) 2011 Devin Bayer
# Copyright (C) 2013 Arthur de Jong
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA

"""webcheck installation script."""

from setuptools import setup, find_packages

from webcheck import __version__, __homepage__


setup(
    name='webcheck',
    version=__version__,
    packages=find_packages(exclude=('sqltap', )),
    package_data={
        'webcheck': [
            'templates/*.html', 'static/*.*', 'static/fancytooltips/*.*',
        ]},
    entry_points={
        'console_scripts': [
            'webcheck = webcheck.cmd:entry_point',
        ],
    },
    install_requires=['setuptools', 'sqlalchemy', 'jinja2'],
    extras_require={
        'tidy': ['utidylib'],
        'soup': ['beautifulsoup'],
    },
    author='Arthur de Jong',
    author_email='arthur@arthurdejong.org',
    description='webcheck is a website checking tool for webmasters',
    license='GPL',
    keywords='spider',
    url=__homepage__,
)
