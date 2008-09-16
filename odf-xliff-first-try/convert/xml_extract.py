#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2002-2006 Zuza Software Foundation
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

class Translatable(object):
    """A node corresponds to a translatable element. A node may
       have children, which correspond to placeables."""
    def __init__(self, placeable_id = -1, placeable_name = None): 
        if placeable_name is not None:
            self.placeable_name = placeable_name
        else:
            self.placeable_name = "<toplevel element>"             
        self.placeable_id = placeable_id
        self.text = [] # A list of Nodes and unicodes
        self.placables = []
        self.xpath = []

class ParseState(object):
    def __init__(self, namespace_table, placeable_table):
        self.namespace_table = namespace_table
        self.placeable_table = placeable_table
        self.placeable_id    = 0
        self.last_node = None
        self.level = 0
        self.xpath = []

def make_translatable(state, placeable_name = None):
    if state.level > 0:
        state.placeable_id += 1
    return Translatable(state.placeable_id, placeable_name)

def process_placeable(dom_node, state):
    placeable = apply(dom_node, state)
    if len(placeable) == 0:
        return make_translatable(state, "placeable")
    elif len(placeable) == 1:
        return placeable[0]
    else:
        print "ERROR: Found more than one translatable element for a single placeable"
        return placeable[0]

def process_placeables(dom_node, state):
    placeables = []
    text = []
    state.level += 1
    for child in dom_node:
        placeable = process_placeable(child, state)
        placeables.append(placeable)
        text.append(placeable.placeable_name)
    state.level -= 1
    return placeables, text

def process_translatable(dom_node, state):
    translatable = make_translatable(state)
    translatable.text.append(dom_node.text)
    placeables, text = process_placeables(dom_node, state)
    translatable.placeables = placeables
    translatable.text.extend(text)
    return [translatable]

def process_children(dom_node, state):
    children = [apply(child, state) for child in dom_node]
    # Flatten a list of lists into a list of elements
    return [child for child_list in children for child in child_list]

def apply(dom_node, state):  
    state.xpath.append(dom_node.tag)
    if dom_node.tag in state.namespace_table:
        result = process_translatable(dom_node, state)
    else:
        result = process_children(dom_node, state)
    state.xpath.pop()
    return result

# ======================

def walk_translatable_tree(translatables, f):
    for translatable in translatables:
        f(translatable)
        walk_translatable_tree(translatable.placeables, f)
        
