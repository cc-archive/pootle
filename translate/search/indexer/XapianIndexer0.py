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

BEWARE: this implementation is BROKEN
    Take a look at "query_parse" below, if you want to fix it.
    As Xapian v0.x is not important for Pootle (as of April 02008), this
    is not likely to be fixed, if _you_ don't do it on your own!
    (sumpfralle)
"""

__revision__ = "$Id$"


import XapianIndexer
import xapian
import re


def is_available():
    #return xapian.major_version() == 0
    # always return False, since the interface is not working
    return False


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
            # TODO: invalid for xapian v0.9
            # a query for "FIELDcontent*" is always empty - this is the
            # show stopper for the xapian v0.9 interface
            return super(Xapian0QueryParser, self).parse_query(
                    str("%s%s" % (prefix, text)), flags)

class Xapian0Query(xapian.Query):
    """ overwrite the __init__ function to allow unicode strings as parameters
    """

    def __init__(self, param1, param2=None):
        if param2 is None:
            super(Xapian0Query, self).__init__(param1)
            return
        if isinstance(param2, unicode):
            param2 = str(param2)
        # TODO: this just removes invalid queries - but it makes any search fail
        # see 'parse_query' above for details
        if isinstance(param2, list):
            param2 = [ q for q in param2 if not q.is_empty() ]
        super(Xapian0Query, self).__init__(param1, param2)


def _xapian0_extract_fieldvalues(match, (result, fieldnames)):
    """ the original '_extract_fieldvalues' function in 'XapianIndexer.py'
    uses 'term.term' instead of 'term[0]'
    """
    # prepare empty dict
    item_fields = {}
    # fill the dict
    for term in match["document"].termlist():
        for fname in fieldnames:
            if ((fname is None) and re.match("[^A-Z]", term[0])):
                value = term[0]
            elif re.match("%s[^A-Z]" % str(fname).upper(), term[0]):
                value = term[0][len(fname):]
            else:
                continue
            # we found a matching field/term
            if item_fields.has_key(fname):
                item_fields[fname].append(value)
            else:
                item_fields[fname] = [value]
    result.append(item_fields)

# don't overwrite the xapian v1.x interface while trying to load xapian0
if is_available():
    xapian.TermGenerator = Xapian0TermGenerator
    xapian.Document = Xapian0Document
    xapian.QueryParser = Xapian0QueryParser
    xapian.Query = Xapian0Query
    xapian.DatabaseOpeningError = Exception
    XapianIndexer._extract_fieldvalues = _xapian0_extract_fieldvalues

