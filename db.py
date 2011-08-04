
# db.py - database access layer for webcheck
#
# Copyright (C) 2011 Arthur de Jong
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

import urlparse

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, Boolean, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.orm.session import object_session
from sqlalchemy.sql.expression import ClauseElement

import config
import debugio
import myurllib


# provide session and schema classes
Session = sessionmaker()
Base = declarative_base()


children = Table(
    'children', Base.metadata,
    Column('parent_id', Integer, ForeignKey('links.id', ondelete='CASCADE')),
    Column('child_id', Integer, ForeignKey('links.id', ondelete='CASCADE'))
    )


embedded = Table(
    'embedded', Base.metadata,
    Column('parent_id', Integer, ForeignKey('links.id', ondelete='CASCADE')),
    Column('child_id', Integer, ForeignKey('links.id', ondelete='CASCADE'))
    )


class Link(Base):

    __tablename__ = 'links'

    id = Column(Integer, primary_key=True)
    url = Column(String, index=True, nullable=False, unique=True)
    fetched = Column(DateTime, index=True)
    is_internal = Column(Boolean, index=True)
    yanked = Column(String, index=True)
    depth = Column(Integer)

    # information about the retrieved link
    status = Column(String)
    mimetype = Column(String)
    mimetype = Column(String)
    encoding = Column(String)
    size = Column(Integer)
    mtime = Column(DateTime)
    is_page = Column(Boolean, index=True)
    title = Column(String)
    author = Column(String)

    # relationships between links
    children = relationship('Link', secondary=children,
        backref=backref('linked_from', collection_class=set),
        primaryjoin=(id == children.c.parent_id),
        secondaryjoin=(id == children.c.child_id),
        collection_class=set)
    embedded = relationship('Link', secondary=embedded,
        backref=backref('embedded_in', collection_class=set),
        primaryjoin=(id == embedded.c.parent_id),
        secondaryjoin=(id == embedded.c.child_id),
        collection_class=set)

    # crawling information
    redirectdepth = Column(Integer, default=0)

    @staticmethod
    def clean_url(url):
        # normalise the URL, removing the fragment from the URL
        url = myurllib.normalizeurl(url)
        (scheme, netloc, path, query) = urlparse.urlsplit(url)[0:4]
        return urlparse.urlunsplit((scheme, netloc, path, query, ''))

    def _get_link(self, url):
        """Get a link object for the specified URL."""
        # get the session
        session = object_session(self)
        # try to find the URL
        url = self.clean_url(url)
        instance = session.query(Link).filter_by(url=url).first()
        if not instance:
            instance = Link(url=url)
            session.add(instance)
        return instance

    def set_encoding(self, encoding):
        """Set the encoding of the link doing some basic checks to see if
        the encoding is supported."""
        if not self.encoding and encoding:
            try:
                debugio.debug('crawler.Link.set_encoding(%r)' % encoding)
                unicode('just some random text', encoding, 'replace')
                self.encoding = encoding
            except Exception, e:
                import traceback
                traceback.print_exc()
                self.add_pageproblem('unknown encoding: %s' % encoding)

    def add_redirect(self, url):
        """Indicate that this link redirects to the specified url."""
        url = self.clean_url(url)
        # figure out depth
        self.redirectdepth = max([self.redirectdepth] +
                                 [x.redirectdepth for x in self.parents]) + 1
        # check depth
        if self.redirectdepth >= config.REDIRECT_DEPTH:
            self.add_linkproblem('too many redirects (%d)' % self.redirectdepth)
            return
        # check for redirect to self
        if url == self.url:
            self.add_linkproblem('redirect same as source: %s' % url)
            return
        # add child
        self.add_child(url)

    def add_linkproblem(self, message):
        """Indicate that something went wrong while retrieving this link."""
        self.linkproblems.append(LinkProblem(message=message))

    def add_pageproblem(self, message):
        """Indicate that something went wrong with parsing the document."""
        # only think about problems on internal pages
        if not self.is_internal:
            return
        # TODO: only include a single problem once (e.g. multiple anchors)
        self.pageproblems.append(PageProblem(message=message))

    def add_child(self, url):
        """Add the specified URL as a child of this link."""
        # ignore children for external links
        if not self.is_internal:
            return
        # add to children
        self.children.add(self._get_link(url))

    def add_embed(self, url):
        """Mark the given URL as used as an image on this page."""
        # ignore embeds for external links
        if not self.is_internal:
            return
        # add to embedded
        self.embedded.add(self._get_link(url))

    def add_anchor(self, anchor):
        """Indicate that this page contains the specified anchor."""
        return # FIXME: implement/update
        # lowercase anchor
        anchor = anchor.lower()
        # add anchor
        if anchor in self.anchors:
            self.add_pageproblem(
              'anchor/id "%(anchor)s" defined multiple times'
              % { 'anchor':   anchor })
        else:
            self.anchors.add(anchor)

    def add_reqanchor(self, parent, anchor):
        """Indicate that the specified link contains a reference to the
        specified anchor. This can be checked later."""
        return # FIXME: implement/update
        # lowercase anchor
        anchor = anchor.lower()
        # convert the url to a link object if we were called with a url
        parent = self.__tolink(parent)
        # add anchor
        if anchor in self.reqanchors:
            if parent not in self.reqanchors[anchor]:
                self.reqanchors[anchor].add(parent)
        else:
            self.reqanchors[anchor] = set([parent])

    def follow_link(self, visited=None):
        """If this link represents a redirect return the redirect target,
        otherwise return self. If this redirect does not find a referenced
        link None is returned."""
        # if this is not a redirect just return
        if not self.redirectdepth:
            return self
        # if we don't know where this redirects, return None
        if not self.children:
            return None
        # avoid loops
        if not visited:
            visited = set()
        visited.add(self.url)
        # the first (and only) child is the redirect target
        child = list(self.children)[0]
        if child.url in visited:
            return None
        # check where we redirect to
        return child.follow_link(visited)

    @property
    def parents(self):
        return set(self.linked_from).union(self.embedded_in)


class LinkProblem(Base):
    """Storage of problems in the URL itself (e.g. problem downloading the
    associated resource)."""

    __tablename__ = 'linkproblems'

    id = Column(Integer, primary_key=True)
    link_id = Column(Integer, ForeignKey('links.id', ondelete='CASCADE'))
    link = relationship(Link, backref=backref('linkproblems', order_by=id,
                        cascade='all,delete,delete-orphan'))
    message = Column(String)

    def __unicode__(self):
        return self.message


class PageProblem(Base):
    """Storage of problems in the information from the retrieved URL (e.g.
    invalid HTML)."""

    __tablename__ = 'pageproblems'

    id = Column(Integer, primary_key=True)
    link_id = Column(Integer, ForeignKey('links.id', ondelete='CASCADE'))
    link = relationship(Link, backref=backref('pageproblems', order_by=id,
                        cascade='all,delete,delete-orphan'))
    message = Column(String)

    def __unicode__(self):
        return self.message
