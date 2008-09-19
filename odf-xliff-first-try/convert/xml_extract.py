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

class XPathBreadcrumb(object):
    def __init__(self):
        self._xpath = []
        self._tagtally = [{}]
        
    def start_tag(self, tag):
        tally_dict = self._tagtally[-1]
        tally = tally_dict.get(tag, -1) + 1
        tally_dict[tag] = tally
        self._xpath.append((tag, tally))
        self._tagtally.append({})
      
    def end_tag(self):
        self._xpath.pop()
        self._tagtally.pop()

    def _get_xpath(self):
        def str_component(component):
            tag, pos = component
            return "%s[%d]" % (tag, pos)
        return "/".join(str_component(component) for component in self._xpath)
    
    xpath = property(_get_xpath)

class Translatable(object):
    """A node corresponds to a translatable element. A node may
       have children, which correspond to placeables."""
    def __init__(self, placeable_id, placeable_name): 
        self.placeable_name = placeable_name
        self.placeable_id = placeable_id
        self.text = [] # A list of Nodes and unicodes
        self.placeables = []
        self.xpath = ""

class ParseState(object):
    def __init__(self, namespace_table, placeable_table):
        self.namespace_table = namespace_table
        self.placeable_table = placeable_table
        self.placeable_id    = 0
        self.last_node = None
        self.level = 0
        self.xpath_breadcrumb = XPathBreadcrumb()
        self.placeable_name = ["<top-level>"]

def make_translatable(state, placeable_name = None):
    if state.level > 0:
        state.placeable_id += 1
        return Translatable(state.placeable_id, placeable_name)
    else:
        return Translatable(-1, placeable_name)
      
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
        text.extend([placeable, child.tail or u""])
    state.level -= 1
    return placeables, text

def process_translatable(dom_node, state):
    translatable = make_translatable(state, state.placeable_name[-1])
    translatable.text.append(dom_node.text or u"")
    placeables, text = process_placeables(dom_node, state)
    translatable.placeables = placeables
    translatable.text.extend(text)
    translatable.xpath = state.xpath_breadcrumb.xpath
    return [translatable]

def process_children(dom_node, state):
    children = [apply(child, state) for child in dom_node]
    # Flatten a list of lists into a list of elements
    return [child for child_list in children for child in child_list]

def apply(dom_node, state):  
    state.xpath_breadcrumb.start_tag(dom_node.tag)
    if dom_node.tag in state.placeable_table:
        state.placeable_name.append(state.placeable_table[dom_node.tag])
    if dom_node.tag in state.namespace_table:
        result = process_translatable(dom_node, state)
    else:
        result = process_children(dom_node, state)
    if dom_node.tag in state.placeable_table:
        state.placeable_name.pop()
    state.xpath_breadcrumb.end_tag()
    return result

# ======================

def make_store_adder(store):
    UnitClass = store.UnitClass
    def add_to_store(translatable):
        source_text = []
        for component in translatable.text:
            if isinstance(component, Translatable):
                placeable_text = u"[[[%(placeable_name)s_%(placeable_id)d]]]" % component.__dict__
                source_text.append(placeable_text)
            else:
                source_text.append(component)
        unit = UnitClass(u''.join(source_text))
        unit.addlocation(translatable.xpath)
        if translatable.placeable_id > -1:
            unit.addnote("References: %(placeable_id)d" % translatable.__dict__)
        store.addunit(unit)
    return add_to_store

def walk_translatable_tree(translatables, f):
    for translatable in translatables:
        f(translatable)
        walk_translatable_tree(translatable.placeables, f)
        
