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

import lxml.etree as etree

from context import with_context

import odf_shared

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
    def level_enter():
        state.level += 1
        
    def level_exit():
        state.level -= 1

    placeables = []
    text = []
    def with_block(level):
        for child in dom_node:
            placeable = process_placeable(child, state)
            placeables.append(placeable)
            text.extend([placeable, child.tail or u""])
        return placeables, text
    return with_context(level_enter, level_exit, with_block)

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
    def xpath_enter():
        state.xpath_breadcrumb.start_tag(dom_node.tag)
      
    def xpath_exit():
        state.xpath_breadcrumb.end_tag()
        
    def placeable_enter():
        if dom_node.tag in state.placeable_table:
            state.placeable_name.append(state.placeable_table[dom_node.tag])
            
    def placeable_exit():
        if dom_node.tag in state.placeable_table:
            state.placeable_name.pop()
  
    def with_block(None_):
        def with_block(None_):
            if dom_node.tag in state.namespace_table:
                return process_translatable(dom_node, state)
            else:
                return process_children(dom_node, state)            
        return with_context(placeable_enter, placeable_exit, with_block)
    return with_context(xpath_enter, xpath_exit, with_block)

# ======================

def make_store_adder(store):
    UnitClass = store.UnitClass
    def add_to_store(translatable):
        source_text = []
        if translatable.text in ([u""], []):
            return
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

def as_file(obj):
    if isinstance(obj, (str, unicode)):
        return open(obj)
    else:
        return obj

def build_store(odf_filename, store):
    """Utility function for loading xml_filename"""        
    tree = etree.parse(as_file(odf_filename))
    parse_state = ParseState(odf_shared.odf_namespace_table, odf_shared.odf_placables_table)
    root = tree.getroot()
    translatables = apply(root, parse_state)
    walk_translatable_tree(translatables, make_store_adder(store))
        
# ======================

class XPathTree(object):
    def __init__(self, unit = None):
        self.unit = unit
        self.children = {}

def split_xpath_component(xpath_component):
    """Split an xpath component into a tag-index tuple.
     
    >>> split_xpath_component('{urn:oasis:names:tc:opendocument:xmlns:office:1.0}document-content[0]')
    ('{urn:oasis:names:tc:opendocument:xmlns:office:1.0}document-content', 0).
    """
    lbrac = xpath_component.rfind(u'[')
    rbrac = xpath_component.rfind(u']')
    tag   = xpath_component[:lbrac]
    index = int(xpath_component[lbrac+1:rbrac])
    return tag, index

def split_xpath(xpath):
    """Split an 'xpath' string separated by / into a reversed list of its components. Thus:
    
    >>> split_xpath('document-content[1]/body[2]/text[3]/p[4]')
    [('p', 4), ('text', 3), ('body', 2), ('document-content', 1)]
    
    The list is reversed so that it can be used as a stack, where the top of the stack is
    the first component.
    """
    components = xpath.split(u'/')
    components = [split_xpath_component(component) for component in components]
    return list(reversed(components))

def add_unit_to_tree(node, xpath_components, unit):
    """Walk down the tree rooted a node, and follow nodes which correspond to the
    components of xpath_components. When reaching the end of xpath_components,
    set the reference of the node to unit.
    
    With reference to the tree diagram in build_unit_tree, 
      
      add_unit_to_tree(node, [('p', 2), ('text', 3), ('body', 2), ('document-content', 1)], unit)
    
    would begin by popping ('document-content', 1) from the path and following the node marked
    ('document-content', 1) in the tree. Likewise, will descend down the nodes marked ('body', 2) 
    and ('text', 3).
    
    Since the node marked ('text', 3) has no child node marked ('p', 2), this node is created. Then
    the add_unit_to_tree descends down this node. When this happens, there are no xpath components
    left to pop. Thus, node.unit = unit is executed. 
    """
    if len(xpath_components) > 0:
        component = xpath_components.pop() # pop the stack; is a component such as ('p', 4)
        # if the current node does not have any children indexed by 
        # the current component, add such a child
        if component not in node.children: 
            node.children[component] = XPathTree()
        add_unit_to_tree(node.children[component], xpath_components, unit)
    else:
        node.unit = unit

def build_unit_tree(store):
    """Enumerate a translation store and build a tree with XPath components as nodes
    and where a node contains a unit if a path from the root of the tree to the node
    containing the unit, is equal to the XPath of the unit.
    
    The tree looks something like this:
    
    root
       `- ('document-content', 1)
          `- ('body', 2)
             |- ('text', 1)
             |  `- ('p', 1)
             |     `- <reference to a unit>
             |- ('text', 2)
             |  `- ('p', 1)
             |     `- <reference to a unit>
             `- ('text', 3)
                `- ('p', 1)
                   `- <reference to a unit>
    """
    tree = XPathTree()
    for unit in store.units:
        location = split_xpath(unit.getlocations()[0])
        add_unit_to_tree(tree, location, unit)
    return tree

def get_tag_arrays(dom_node):
    """Return a dictionary indexed by child tag names, where each tag is associated with an array
    of all the child nodes with matching the tag name, in the order in which they appear as children
    of dom_node.
    
    >>> xml = '<a><b></b><c></c><b></b><d/></a>'
    >>> element = etree.fromstring(xml)
    >>> get_tag_arrays(element)
    {'b': [<Element a at 84df144>, <Element a at 84df148>], 'c': [<Element a at 84df120>], 'd': [<Element a at 84df152>]}
    """
    child_dict = {}
    for child in dom_node:
        if child.tag not in child_dict:
            child_dict[child.tag] = []
        child_dict[child.tag].append(child)
    return child_dict

def apply_translations(dom_node, unit_node, do_translate):
    # If there is a translation unit associated with this unit_node...
    if unit_node.unit != None:
        # The invoke do_translate on the dom_node and the unit; do_translate
        # should replace the text in dom_node with the text in unit_node.
        do_translate(dom_node, unit_node.unit)
    tag_array = get_tag_arrays(dom_node)
    for unit_child_index, unit_child in unit_node.children.iteritems():
        tag, index = unit_child_index
        try:
            dom_child = tag_array[tag][index]
            apply_translations(dom_child, unit_child, do_translate)
        # Raised if tag is not in tag_array. We might want to complain to the
        # user in the future.
        except KeyError:
            pass
        # Raised if index is not in tag_array[tag]. We might want to complain to
        # the user in the future
        except IndexError:
            pass
