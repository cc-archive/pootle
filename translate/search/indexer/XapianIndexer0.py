#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008 Zuza Software Foundation
# 
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

"""
interface to the xapian indexing engine for the translate toolkit

Xapian v0.x is supported.
See XapianIndexer.py for an interface for Xapian v1.0 and higher.
"""

__revision__ = "$Id$"


import XapianIndexer
import xapian
import re


def is_available():
    return xapian.major_version() == 0


from XapianIndexer import _truncate_term_length 


""" difference between Xapian v0.x and v1.x:
    * xapian.TermGenerator is missing in releases before v1.0
    * xapian.Document.add_term accepts only string (not unicode)
    * xapian.Query.__init__ accepts only string (not unicode)
    * xapian.QueryParser does not handle FLAG_PARTIAL
"""


""" inherit the following two classes instead of importing
This clarifies the output of "test_indexers.py".
"""
class XapianDatabase0(XapianIndexer.XapianDatabase):
    pass

class XapianEnquire0(XapianIndexer.XapianEnquire):
    pass


class Xapian0TermGenerator:
    """ implement the basic functions of the Xapian v1.x TermGenerator class

    functions used by pootle:
        * set_document(xapian.Document)
        * index_text(str)
    """

    def set_document(self, doc):
        self.document = doc


    def index_text(self, text, weight=1, prefix=""):
        # weight is ignored
        terms = re.sub(u'\W', ' ', text).split(" ")
        for term in terms:
            self.document.add_term(_truncate_term_length(str("%s%s" % (prefix, term))))


class Xapian0Document(xapian.Document):
    """ overwrite the function 'add_term' to allow unicode strings as parameter
    """

    def add_term(self, text):
        return super(Xapian0Document, self).add_term(str(text))

class Xapian0QueryParser(xapian.QueryParser):
    """ overwrite the function 'parse_query' to add support for FLAG_PARTIAL
    """

    # taken from xapian v1.x
    FLAG_PARTIAL = 64

    def parse_query(self, text, flags, prefix=None):
	if flags & self.FLAG_PARTIAL > 0:
            text += "*"
            flags &= ~self.FLAG_PARTIAL
            flags |= self.FLAG_WILDCARD
        if prefix is None:
            return super(Xapian0QueryParser, self).parse_query(text, flags)
        else:
            return super(Xapian0QueryParser, self).parse_query(
                "%s%s" % (prefix, text), flags)

class Xapian0Query(xapian.Query):
    """ overwrite the __init__ function to allow unicode strings as parameters
    """

    def __init__(self, param1, param2=None):
        if param2 is None:
            super(Xapian0Query, self).__init__(param1)
            return
        if isinstance(param2, unicode):
            param2 = str(param2)
        super(Xapian0Query, self).__init__(param1, param2)


xapian.TermGenerator = Xapian0TermGenerator
xapian.Document = Xapian0Document
xapian.QueryParser = Xapian0QueryParser
xapian.Query = Xapian0Query

