
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

import logging
import urlparse

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import distinct, func
from sqlalchemy import Table, Column, Integer, Boolean, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.orm.session import object_session
from sqlalchemy.sql.expression import union

from webcheck import config
from webcheck.myurllib import normalizeurl


logger = logging.getLogger(__name__)



# provide session and schema classes
Session = sessionmaker()
Base = declarative_base()


children = Table(
    'children', Base.metadata,
    Column('parent_id', Integer, ForeignKey('links.id', ondelete='CASCADE'), index=True),
    Column('child_id', Integer, ForeignKey('links.id', ondelete='CASCADE'), index=True)
    )


embedded = Table(
    'embedded', Base.metadata,
    Column('parent_id', Integer, ForeignKey('links.id', ondelete='CASCADE'), index=True),
    Column('child_id', Integer, ForeignKey('links.id', ondelete='CASCADE'), index=True)
    )


class Link(Base):

    __tablename__ = 'links'

    id = Column(Integer, primary_key=True)
    url = Column(String, index=True, nullable=False, unique=True)
    is_internal = Column(Boolean, index=True)
    yanked = Column(String, index=True)
    fetched = Column(DateTime, index=True)

    # information about the retrieved link
    status = Column(String)
    mimetype = Column(String)
    mimetype = Column(String)
    encoding = Column(String)
    size = Column(Integer)
    mtime = Column(DateTime, index=True)
    is_page = Column(Boolean, index=True)
    title = Column(String, index=True)
    author = Column(String)

    # relationships between links
    children = relationship('Link', secondary=children,
        backref=backref('linked_from', lazy='dynamic'),
        primaryjoin=(id == children.c.parent_id),
        secondaryjoin=(id == children.c.child_id),
        lazy='dynamic')
    embedded = relationship('Link', secondary=embedded,
        backref=backref('embedded_in', lazy='dynamic'),
        primaryjoin=(id == embedded.c.parent_id),
        secondaryjoin=(id == embedded.c.child_id),
        lazy='dynamic')

    # crawling information
    redirectdepth = Column(Integer, default=0)
    depth = Column(Integer, default=0)

    @staticmethod
    def clean_url(url):
        # normalise the URL, removing the fragment from the URL
        return urlparse.urldefrag(normalizeurl(url))[0]

    def _get_link(self, url):
        """Get a link object for the specified URL."""
        # get the session
        session = object_session(self)
        # normalise the URL, removing the fragment from the URL
        url, fragment = urlparse.urldefrag(normalizeurl(url))
        # try to find the link
        instance = session.query(Link).filter_by(url=url).first()
        if not instance:
            if config.MAX_DEPTH and self.depth >= config.MAX_DEPTH:
                logger.debug('link %s too deep', url)
            instance = Link(url=url, depth=self.depth + 1)
            session.add(instance)
        else:
            # we may have discovered a shorter path
            instance.depth = min(instance.depth, self.depth + 1)
        # mark that we were looking for an anchor/fragment
        if fragment:
            instance.add_reqanchor(self, fragment)
        # return the link
        return instance

    def set_encoding(self, encoding):
        """Set the encoding of the link doing some basic checks to see if
        the encoding is supported."""
        if not self.encoding and encoding:
            try:
                logger.debug('crawler.Link.set_encoding(%r)', encoding)
                unicode('just some random text', encoding, 'replace')
                self.encoding = encoding
            except Exception, e:
                logger.exception('unknown encoding: %s', encoding)
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
        self.children.append(self._get_link(url))

    def add_embed(self, url):
        """Mark the given URL as used as an image on this page."""
        # ignore embeds for external links
        if not self.is_internal:
            return
        # add to embedded
        self.embedded.append(self._get_link(url))

    def add_anchor(self, anchor):
        """Indicate that this page contains the specified anchor."""
        # lowercase anchor
        anchor = anchor.lower()
        if self.anchors.filter(Anchor.anchor == anchor).first():
            self.add_pageproblem(
              'anchor/id "%(anchor)s" defined multiple times'
              % {'anchor': anchor})
        else:
            self.anchors.append(Anchor(anchor=anchor))

    def add_reqanchor(self, parent, anchor):
        """Indicate that the specified link contains a reference to the
        specified anchor. This can be checked later."""
        # lowercase anchor
        anchor = anchor.lower()
        # if RequestedAnchor doesn't exist, add it
        if not self.reqanchors.filter((RequestedAnchor.parent_id == parent.id) & (RequestedAnchor.anchor == anchor)).first():
            self.reqanchors.append(RequestedAnchor(parent_id=parent.id, anchor=anchor))

    def follow_link(self, visited=None):
        """If this link represents a redirect return the redirect target,
        otherwise return self. If this redirect does not find a referenced
        link None is returned."""
        # if this is not a redirect just return
        if not self.redirectdepth:
            return self
        # if we don't know where this redirects, return None
        if not self.children.count():
            return None
        # avoid loops
        if not visited:
            visited = set()
        visited.add(self.url)
        # the first (and only) child is the redirect target
        child = self.children.first()
        if child.url in visited:
            return None
        # check where we redirect to
        return child.follow_link(visited)

    @property
    def count_parents(self):
        session = object_session(self)
        p1 = session.query(func.count(distinct(children.c.parent_id))).filter(children.c.child_id == self.id)
        p2 = session.query(func.count(distinct(embedded.c.parent_id))).filter(embedded.c.child_id == self.id)
        return p1.scalar() + p2.scalar()

    @property
    def parents(self):
        session = object_session(self)
        #links = object_session(self).query(Link)
        #links = links.join(children, Link.id == children.c.parent_id)
        #links = links.join(embedded, Link.id == embedded.c.parent_id)
        #return links.filter((children.c.child_id == self.id) |
        #                    (embedded.c.child_id == self.id)).distinct()
        parent_ids = union(session.query(children.c.parent_id).filter(children.c.child_id == self.id),
                           session.query(embedded.c.parent_id).filter(embedded.c.child_id == self.id))

        return session.query(Link).filter(Link.id == parent_ids.c.children_parent_id).distinct()


class LinkProblem(Base):
    """Storage of problems in the URL itself (e.g. problem downloading the
    associated resource)."""

    __tablename__ = 'linkproblems'

    id = Column(Integer, primary_key=True)
    link_id = Column(Integer, ForeignKey('links.id', ondelete='CASCADE'), index=True)
    message = Column(String, index=True)
    link = relationship(Link, backref=backref('linkproblems', order_by=message,
                        cascade='all,delete,delete-orphan'))

    def __unicode__(self):
        return self.message


class PageProblem(Base):
    """Storage of problems in the information from the retrieved URL (e.g.
    invalid HTML)."""

    __tablename__ = 'pageproblems'

    id = Column(Integer, primary_key=True)
    link_id = Column(Integer, ForeignKey('links.id', ondelete='CASCADE'), index=True)
    message = Column(String, index=True)
    link = relationship(Link, backref=backref('pageproblems', order_by=message,
                        cascade='all,delete,delete-orphan'))

    def __unicode__(self):
        return self.message


class Anchor(Base):
    """The named anchors (IDs) found on the page."""

    __tablename__ = 'anchors'

    id = Column(Integer, primary_key=True)
    link_id = Column(Integer, ForeignKey('links.id', ondelete='CASCADE'), index=True)
    link = relationship(Link, backref=backref('anchors',
                        lazy='dynamic',
                        cascade='all,delete,delete-orphan'))
    anchor = Column(String)

    def __unicode__(self):
        return self.anchor


class RequestedAnchor(Base):
    """The named anchors (IDs) found on the page."""

    __tablename__ = 'reqanchors'

    id = Column(Integer, primary_key=True)
    link_id = Column(Integer, ForeignKey('links.id', ondelete='CASCADE'), index=True)
    link = relationship(Link, backref=backref('reqanchors',
                        lazy='dynamic',
                        cascade='all,delete,delete-orphan',
                        ), primaryjoin='Link.id == RequestedAnchor.link_id')
    parent_id = Column(Integer, ForeignKey('links.id', ondelete='CASCADE'), index=True)
    parent = relationship(Link, primaryjoin='Link.id == RequestedAnchor.parent_id')
    anchor = Column(String)

    def __unicode__(self):
        return self.anchor


def truncate_db():
    """Clear all tables in the database."""
    session = Session()
    session.query(LinkProblem).delete()
    session.commit()
    session.query(PageProblem).delete()
    session.commit()
    session.query(Anchor).delete()
    session.commit()
    session.query(RequestedAnchor).delete()
    session.commit()
    session.execute(children.delete())
    session.commit()
    session.execute(embedded.delete())
    session.commit()
    session.query(Link).delete()
    session.commit()
