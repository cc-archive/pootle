#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008-2009 Zuza Software Foundation
#
# This file is part of the Translate Toolkit.
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
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""
Contains the C{parse} function that parses normal strings into StringElem-
based "rich" string element trees.
"""

from translate.storage.placeables import base, StringElem


def parse(tree, parse_funcs):
    """Parse placeables from the given string or sub-tree by using the
        parsing functions provided.

        The output of this function is B{heavily} dependent on the order of the
        parsing functions. This is because of the algorithm used.

        An over-simplification of the algorithm: the leaves in the C{StringElem}
        tree are expanded to the output of the first parsing function in
        C{parse_funcs}. The next level of recursion is then started on the new
        set of leaves with the used parsing function removed from
        C{parse_funcs}.

        @type  tree: str|unicode|StringElem
        @param tree: The string or string element sub-tree to parse.
        @type  parse_funcs: A list of parsing functions. It must take exactly
            one argument (a C{unicode} string to parse) and return a list of
            C{StringElem}s which, together, form the original string. If nothing
            could be parsed, it should return C{None}."""
    if isinstance(tree, (str, unicode)):
        tree = StringElem([tree])
    if not parse_funcs:
        return tree
    leaves = [elem for elem in tree.depth_first() if elem.isleaf()]
    parse_func = parse_funcs[0]

    for leaf in leaves:
        if not unicode(leaf):
            continue
        subleaves = parse_func(unicode(leaf))
        if subleaves is not None:
            leaf.sub = subleaves
        parse(leaf, parse_funcs[1:])

        # The rest of this block handles the case in which a StringElem was created by a previous
        # parsing function and a later one added a StringElem sub-class as a child which consumes
        # the whole string. That means that the leaf was changed from a StringElem with a single
        # (unicode) sub-element to a StringElem with a single StringElemSubClass element which, in
        # turn has a single unicode sub-element, equal to the original StringElem's.
        # Simbolically it does StringElem([StringElemSubClass(['foo'])]) ->  StringElemSubClass(['foo'])
        if len(leaf.sub) == 1 and \
                type(leaf) is StringElem and \
                type(leaf.sub[0]) is not StringElem and \
                isinstance(leaf.sub[0], StringElem):
            parent = tree.get_parent_elem(leaf)
            if parent is not None:
                leafindex = parent.sub.index(leaf)
                parent.sub[leafindex] = leaf.sub[0]
    return tree
