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

import re

import lxml.etree as etree

from translate.storage import base

from translate.misc.context import with_
from translate.misc.contextlib import contextmanager, nested
from translate.misc.typecheck import accepts, Self, IsCallable, IsOneOf
from translate.misc.typecheck.typeclasses import Number

import odf_shared

class XPathBreadcrumb(object):
    """A class which is used to build XPath-like paths as a DOM tree is
    walked. It keeps track of the number of times which it has seen
    a certain tag, so that it will correctly create indices for tags.
    
    Initially, the path is empty. Thus
    >>> xb = XPathBreadcrumb()
    >>> xb.xpath
    ""
    
    Suppose we walk down a DOM node for the tag <foo> and we want to
    record this, we simply do
    >>> xb.start_tag('foo')
    
    Now, the path is no longer empty. Thus
    >>> xb.xpath
    foo[0]
    
    Now suppose there are two <bar> tags under the tag <foo> (that is
    <foo><bar></bar><bar></bar><foo>), then the breadcrumb will keep
    track of the number of times it sees <bar>. Thus
    
    >>> xb.start_tag('bar')
    >>> xb.xpath
    foo[0]/bar[0]
    >>> xb.end_tag()
    >>> xb.xpath
    foo[0]
    >>> xb.start_tag('bar')
    >>> xb.xpath
    foo[0]/bar[1]
    """

    def __init__(self):
        self._xpath = []
        self._tagtally = [{}]
        
    @accepts(Self(), unicode)
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
            return u"%s[%d]" % (tag, pos)
        return u"/".join(str_component(component) for component in self._xpath)
    
    xpath = property(_get_xpath)

class Translatable(object):
    """A node corresponds to a translatable element. A node may
       have children, which correspond to placeables."""
    def __init__(self, placeable_id, placeable_name): 
        self.placeable_name = placeable_name
        self.placeable_id = placeable_id
        self.placeable_tag_id = 1
        self.source = []
        self.xpath = ""
        self.is_inline = False

    def _get_placeables(self):
        return [placeable for placeable in self.source if isinstance(placeable, Translatable)]

    placeables = property(_get_placeables)

class ParseState(object):
    """Maintain constants and variables used during the walking of a
    DOM tree (via the function apply)."""
    def __init__(self, namespace_table, placeable_table = {}, inline_placeable_table = {}):
        self.namespace_table = namespace_table
        self.placeable_table = placeable_table
        self.inline_placeable_table = inline_placeable_table
        self.placeable_id = 0
        self.level = 0
        self.is_inline = False
        self.xpath_breadcrumb = XPathBreadcrumb()
        self.placeable_name = [u"<top-level>"]

@accepts(ParseState, unicode)
def make_translatable(state, placeable_name = None):
    """Make a Translatable object. If we are in a placeable (this
    is true if state.level > 0, then increase state.placeable by 1
    and return a Translatable with that placeable ID.
    
    Otherwise we are processing a top-level element, and we give
    it a placeable_id of -1."""
    if state.level > 0:
        state.placeable_id += 1
        return Translatable(state.placeable_id, placeable_name)
    else:
        return Translatable(-1, placeable_name)

@accepts(etree._Element, ParseState)
def process_placeable(dom_node, state):    
    placeable = apply(dom_node, state)
    # This happens if there were no recognized child tags and thus
    # no translatable is returned. Make a placeable with the name
    # "placeable"
    if len(placeable) == 0:
        return make_translatable(state, u"placeable")
    # The ideal situation: we got exactly one translateable back
    # when processing this tree.
    elif len(placeable) == 1:
        return placeable[0]
    # This is bad. This means that there are two or more translateables
    # competing to be the current placeable. This means that further
    # down in the tree, another tag should be handled as a translateable
    # with a number of placealbes, and that translateable would be the
    # placeable in which we are interested here.
    else:
        print "ERROR: Found more than one translatable element for a single placeable"
        return placeable[0]

@accepts(etree._Element, ParseState)
def process_placeables(dom_node, state, source):
    """Return a list of placeables and list with
    alternating string-placeable objects. The former is
    useful for directly working with placeables and the latter
    is what will be used to build the final translatable string."""

    @contextmanager
    def set_level():
        state.level += 1
        yield state.level
        state.level -= 1
    
    def with_block(level):
        source = []
        for child in dom_node:
            source.extend([process_placeable(child, state), unicode(child.tail or u"")])
        return source
    # Do the work within a context to ensure that the level is
    # reset, come what may.
    return with_(set_level(), with_block)

@accepts(etree._Element, ParseState)
def process_translatable(dom_node, state):
    translatable = make_translatable(state, state.placeable_name[-1])
    translatable.source = [unicode(dom_node.text or u"")] + \
                           process_placeables(dom_node, state, translatable.source)
    translatable.xpath = state.xpath_breadcrumb.xpath
    translatable.is_inline = state.is_inline
    return [translatable]

@accepts(etree._Element, ParseState)
def process_children(dom_node, state):
    children = [apply(child, state) for child in dom_node]
    # Flatten a list of lists into a list of elements
    return [child for child_list in children for child in child_list]

@accepts(etree._Element, ParseState)
def apply(dom_node, state):
    @contextmanager
    def xpath_set():
        state.xpath_breadcrumb.start_tag(unicode(dom_node.tag))
        yield state.xpath_breadcrumb
        state.xpath_breadcrumb.end_tag()
        
    @contextmanager
    def placeable_set():
        if dom_node.tag in state.placeable_table:
            state.placeable_name.append(state.placeable_table[dom_node.tag])
            yield state.placeable_name
            state.placeable_name.pop()
        else:
            yield state.placeable_name
            
    @contextmanager
    def inline_set():
        old_inline = state.is_inline
        if dom_node.tag in state.inline_placeable_table:
            state.is_inline = True
        yield state.is_inline
        state.is_inline = old_inline
      
    def with_block(xpath_breadcrumb, placeable_name, is_inline):
        if dom_node.tag in state.namespace_table:
            return process_translatable(dom_node, state)
        else:
            return process_children(dom_node, state)            
    return with_(nested(xpath_set(), placeable_set(), inline_set()), with_block)

# ======================

#def quote_placables(placeable_name, placeable_id):
#    return u"[[[%s_%d]]]" % (placeable_name, placeable_id)

def contains_no_translatable_text(translatable):
    return translatable.source in ([u""], [])

#def tag(tag_name, **attribs):
#    tag_text = [u'<%(tag_name)s']
#    for attrib_key, attrib_val in attribs.iteritems():
#        tag_text.append(u'%s="%s"' % (attrib_key, attrib_val))
#    tag_text.append(u'/>')
#    return u' '.join(tag_text)

#def get_source_text(translatable, placeable_quoter):
#    source_text = []
#    for component in translatable.text:
#        if isinstance(component, Translatable):
#            #source_text.append(tag('bx', id=))
#          
#            source_text.append(placeable_quoter(component.placeable_name, component.placeable_id))
#        else:
#            source_text.append(component)
#    return u''.join(source_text)

def to_string(translatable):
    result = []
    for chunk in translatable.source:
        if isinstance(chunk, unicode):
            result.append(chunk)
        else:
            if chunk.is_inline:
                result.extend([u'<g id="%s">' % chunk.placeable_id, to_string(chunk), u'</g>'])
            else:
                result.append(u'<x id="%s"/>' % chunk.placeable_id)
    return u''.join(result)

def add_location_and_ref_info(unit, translatable):
    unit.addlocation(translatable.xpath)
    if translatable.placeable_id > -1:
        unit.addnote("References: %d" % translatable.placeable_id)
    return unit

@accepts(base.TranslationStore)
def make_store_adder(store):
    """Return a function which, when called with a Translatable will add
    a unit to 'store'. The placeables will represented as strings according
    to 'placeable_quoter'."""
    
    UnitClass = store.UnitClass
    def add_to_store(translatable):
        if contains_no_translatable_text(translatable) or translatable.is_inline:
            return
        unit = UnitClass(to_string(translatable))
        unit = add_location_and_ref_info(unit, translatable)
        store.addunit(unit)
    return add_to_store

@accepts([Translatable], IsCallable())
def walk_translatable_tree(translatables, f):
    for translatable in translatables:
        f(translatable)
        walk_translatable_tree(translatable.placeables, f)

@accepts(lambda obj: hasattr(obj, "read"), base.TranslationStore, IsOneOf(IsCallable(), type(None)))
def build_store(odf_file, store, store_adder = None):
    """Utility function for loading xml_filename"""    
    store_adder = store_adder or make_store_adder(store)
    tree = etree.parse(odf_file)
    parse_state = ParseState(odf_shared.odf_namespace_table, odf_shared.odf_placables_table, odf_shared.odf_inline_placeables_table)
    root = tree.getroot()
    translatables = apply(root, parse_state)
    walk_translatable_tree(translatables, store_adder)
    return tree
        
# ======================

class XPathTree(object):
    @accepts(Self(), base.TranslationUnit)
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

@accepts(unicode)
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

@accepts(etree._Element, [(unicode, Number)], base.TranslationUnit)
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

@accepts(base.TranslationStore)
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

@accepts(etree._Element)
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

@accepts(etree._Element, Translatable, IsCallable())
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

placeable_pattern = re.compile(u'\[\[\[\w+\]\]\]')

def replace_dom_text(dom_node, unit):
    """Use the unit's target (or source in the case where there is no translation)
    to update the text in the dom_node and at the tails of its children."""
    translation = unicode(unit.target or unit.source)
    # This will alter be used to swap around placeables if their positions are changed
    # Search for all the placeables in 'translation'
    _placeable_tokens = placeable_pattern.findall(translation)
    # Split 'translation' into the different chunks of text which
    # run between the placeables.
    non_placeable_chunks = placeable_pattern.split(translation)
    dom_node.text = non_placeable_chunks[0]
    # Assign everything after the first non_placeable to the
    # tails of the child XML nodes (since this is where such text
    # appears).
    for chunk, child in zip(non_placeable_chunks[1:], dom_node):
        child.tail = chunk
