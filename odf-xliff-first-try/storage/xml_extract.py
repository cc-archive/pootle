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

from translate.storage import base

from translate.misc.context import with_
from translate.misc.contextlib import contextmanager, nested
from translate.misc.typecheck import accepts, Self, IsCallable, IsOneOf, Any
from translate.misc.typecheck.typeclasses import Number

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
    @accepts(Self(), Number, unicode)
    def __init__(self, placeable_id, placeable_name): 
        self.placeable_name = placeable_name
        self.placeable_id = placeable_id
        self.placeable_tag_id = 1
        self.source = []
        self.xpath = ""
        self.is_inline = False
        self.dom_node = None

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
def make_translatable(state, placeable_name, dom_node, source):
    """Make a Translatable object. If we are in a placeable (this
    is true if state.level > 0, then increase state.placeable by 1
    and return a Translatable with that placeable ID.
    
    Otherwise we are processing a top-level element, and we give
    it a placeable_id of -1."""
    if state.level > 0:
        state.placeable_id += 1
        translatable = Translatable(state.placeable_id, placeable_name)
    else:
        translatable = Translatable(-1, placeable_name)
    translatable.xpath = state.xpath_breadcrumb.xpath
    translatable.dom_node = dom_node
    translatable.source = source
    return translatable

@accepts(etree._Element, ParseState)
def _process_placeable(dom_node, state):
    """Run find_translatable_dom_nodes on the current dom_node"""
    placeable = find_translatable_dom_nodes(dom_node, state)
    # This happens if there were no recognized child tags and thus
    # no translatable is returned. Make a placeable with the name
    # "placeable"
    if len(placeable) == 0:
        return make_translatable(state, u"placeable", dom_node)
    # The ideal situation: we got exactly one translateable back
    # when processing this tree.
    elif len(placeable) == 1:
        return placeable[0]
    else:
        raise Exception("BUG: find_translatable_dom_nodes should never return more than a single translatable")

@accepts(etree._Element, ParseState)
def _process_placeables(dom_node, state):
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
            source.extend([_process_placeable(child, state), unicode(child.tail or u"")])
        return source
    # Do the work within a context to ensure that the level is
    # reset, come what may.
    return with_(set_level(), with_block)

@accepts(etree._Element, ParseState)
def _process_translatable(dom_node, state):
    source = [unicode(dom_node.text or u"")] + _process_placeables(dom_node, state)
    translatable = make_translatable(state, state.placeable_name[-1], dom_node, source)
    translatable.is_inline = state.is_inline
    return [translatable]

@accepts(etree._Element, ParseState)
def _process_children(dom_node, state):
    children = [find_translatable_dom_nodes(child, state) for child in dom_node]
    # Flatten a list of lists into a list of elements
    children = [child for child_list in children for child in child_list]
    if len(children) > 1:
        intermediate_translatable = make_translatable(state, unicode(dom_node.tag), dom_node, children)
        return [intermediate_translatable]
    else:
        return children

@accepts(etree._Element, ParseState)
def find_translatable_dom_nodes(dom_node, state):
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
            return _process_translatable(dom_node, state)
        else:
            return _process_children(dom_node, state)            
    return with_(nested(xpath_set(), placeable_set(), inline_set()), with_block)

# ======================

@accepts(base.TranslationUnit, Translatable)
def _add_location_and_ref_info(unit, translatable):
    """"""
    unit.addlocation(translatable.xpath)
    if translatable.placeable_id > -1:
        unit.addnote("References: %d" % translatable.placeable_id)
    return unit

@accepts(Translatable)
def _to_string(translatable):
    """Convert a Translatable to an XLIFF string representation."""
    result = []
    for chunk in translatable.source:
        if isinstance(chunk, unicode):
            result.append(chunk)
        else:
            if chunk.is_inline:
                result.extend([u'<g id="%s">' % chunk.placeable_id, _to_string(chunk), u'</g>'])
            else:
                result.append(u'<x id="%s"/>' % chunk.placeable_id)
    return u''.join(result)

@accepts(base.TranslationStore, Translatable)
def _add_translatable_to_store(store, translatable):
    """"""
    unit = store.UnitClass(_to_string(translatable))
    unit = _add_location_and_ref_info(unit, translatable)
    store.addunit(unit)

@accepts(Translatable)
def _contains_translatable_text(translatable):
    """"""
    for chunk in translatable.source:
        if isinstance(chunk, unicode):
            if chunk.strip() != u"":
                return True
    return False

@accepts(base.TranslationStore)
def _make_store_adder(store):
    """Return a function which, when called with a Translatable will add
    a unit to 'store'. The placeables will represented as strings according
    to 'placeable_quoter'."""    
    def add_to_store(translatable):
        if _contains_translatable_text(translatable) and not translatable.is_inline:
            _add_translatable_to_store(store, translatable)
    
    return add_to_store

@accepts([Translatable], IsCallable())
def _walk_translatable_tree(translatables, f):
    """"""
    for translatable in translatables:
        f(translatable)
        _walk_translatable_tree(translatable.placeables, f)

@accepts(lambda obj: hasattr(obj, "read"), base.TranslationStore, IsOneOf(IsCallable(), type(None)))
def build_store(odf_file, store, parse_state, store_adder = None):
    """Utility function for loading xml_filename"""    
    store_adder = store_adder or _make_store_adder(store)
    tree = etree.parse(odf_file)
    root = tree.getroot()
    translatables = find_translatable_dom_nodes(root, parse_state)
    _walk_translatable_tree(translatables, store_adder)
    return tree
        
# ======================

class XPathTree(object):
    @accepts(Self(), base.TranslationUnit)
    def __init__(self, unit = None):
        self.unit = unit
        self.children = {}

@accepts(unicode)
def _split_xpath_component(xpath_component):
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
def _split_xpath(xpath):
    """Split an 'xpath' string separated by / into a reversed list of its components. Thus:
    
    >>> split_xpath('document-content[1]/body[2]/text[3]/p[4]')
    [('p', 4), ('text', 3), ('body', 2), ('document-content', 1)]
    
    The list is reversed so that it can be used as a stack, where the top of the stack is
    the first component.
    """    
    components = xpath.split(u'/')
    components = [_split_xpath_component(component) for component in components]
    return list(reversed(components))

@accepts(etree._Element, [(unicode, Number)], base.TranslationUnit)
def _add_unit_to_tree(node, xpath_components, unit):
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
        _add_unit_to_tree(node.children[component], xpath_components, unit)
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
        location = _split_xpath(unit.getlocations()[0])
        _add_unit_to_tree(tree, location, unit)
    return tree

@accepts(etree._Element)
def _get_tag_arrays(dom_node):
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
    tag_array = _get_tag_arrays(dom_node)
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
    # If there is a translation unit associated with this unit_node...
    if unit_node.unit != None:
        # The invoke do_translate on the dom_node and the unit; do_translate
        # should replace the text in dom_node with the text in unit_node.
        do_translate(dom_node, unit_node.unit)

@accepts(IsCallable(), Any(), Any(), IsCallable(), vargs=[Any()])
def reduce_tree(f, parent_unit_node, unit_node, get_children, *state):
    """Enumerate a tree, applying f to in a pre-order fashion to each node.
    
    parent_unit_node contains the parent of unit_node. For the root of the tree,
    parent_unit_node == unit_node.
    
    get_children is a single argument function applied to a unit_node to
    get a list/iterator to its children.

    state is used by f to modify state information relating to whatever f does
    to the tree.
    """
    def as_tuple(x):
        if isinstance(x, tuple):
            return x
        else:
            return (x,)
    
    state = f(parent_unit_node, unit_node, *state)
    for child_unit_node in get_children(unit_node):
        state = reduce_tree(f, unit_node, child_unit_node, get_children, *as_tuple(state))
    return state

@accepts(IsCallable(), Translatable, vargs=[Any()])
def reduce_unit_tree(f, unit_node, *state):
    return reduce_tree(f, unit_node, unit_node, lambda unit_node: unit_node.placeables, *state)

@accepts(IsCallable(), etree._Element, vargs=[Any()])
def reduce_dom_tree(f, dom_node, *state):
    return reduce_tree(f, dom_node, dom_node, lambda dom_node: dom_node, *state)

@accepts(etree._Element, etree._Element)
def find_dom_root(parent_dom_node, dom_node):
    """@see find_placeable_dom_tree_roots"""
    if dom_node is None or parent_dom_node is None:
        return None
    if dom_node.getparent() == parent_dom_node:
        return dom_node
    elif dom_node.getparent() is None:
        return None
    else:
        return find_dom_root(parent_dom_node, dom_node.getparent())    

@accepts(Translatable)
def find_placeable_dom_tree_roots(unit_node):
    """For an inline placeable, find the root DOM node for the placeable in its
    parent.
    
    Consider the diagram. In this pseudo-ODF example, there is an inline span
    element. However, the span is contained in other tags (which we never process).
    When splicing the template DOM tree (that is, the DOM which comes from 
    the XML document we're using to generate a translated XML document), we'll
    need to move DOM sub-trees around and we need the roots of these sub-trees.
    
    <p> This is text \/                <- Paragraph containing an inline placeable
                     <blah>            <- Inline placeable's root (which we want to find)
                     ...               <- Any number of intermediate DOM nodes
                     <span> bold text  <- The inline placeable's Translatable 
                                          holds a reference to this DOM node    
    """

    def set_dom_root_for_unit_node(parent_unit_node, unit_node, dom_tree_roots):
            dom_tree_roots[unit_node] = find_dom_root(parent_unit_node.dom_node, unit_node.dom_node)
            return dom_tree_roots
    return reduce_unit_tree(set_dom_root_for_unit_node, unit_node, {})
      
@accepts(Translatable, etree._Element)
def _map_source_dom_to_doc_dom(unit_node, source_dom_node):
    """Creating a mapping from the DOM nodes in source_dom_node which correspond to
    placeables, with DOM nodes in the XML document template (this information is obtained
    from unit_node). We are interested in DOM nodes in the XML document template which
    are the roots of placeables. @see the diagram below, as well as 
    find_placeable_dom_tree_roots.
    
    XLIFF Source (below)
    <source>This is text <g> bold text</g> and a footnote<x/></source> 
                         /                                 \________
                        /                                           \
    <p>This is text<blah>...<span> bold text</span>...</blah> and <note>...</note></p>
    Input XML document used as a template (above)
    
    In the above diagram, the XLIFF source DOM node <g> is associated with the XML 
    document DOM node <blah>, whereas the XLIFF source DOM node <x> is associated with
    the XML document DOM node <note>.
    """
    dom_tree_roots = find_placeable_dom_tree_roots(unit_node)
    source_dom_to_doc_dom = {}
  
    def loop(unit_node, source_dom_node):
        for child_unit_node, child_source_dom in zip(unit_node.placeables, source_dom_node):
            source_dom_to_doc_dom[child_source_dom] = dom_tree_roots[child_unit_node]
            loop(child_unit_node, child_source_dom)
    
    loop(unit_node, source_dom_node)
    return source_dom_to_doc_dom

@accepts(etree._Element, etree._Element)
def _map_target_dom_to_source_dom(source_dom_node, target_dom_node):
    def map_id_to_dom_node(parent_node, node, id_to_dom_node):
        if u'id' in node.attrib:
            id_to_dom_node[node.attrib[u'id']] = node
        return id_to_dom_node
    
    id_to_dom_node = reduce_dom_tree(map_id_to_dom_node, target_dom_node, {})
    
    def map_target_dom_to_source_dom_aux(parent_node, node, target_dom_to_source_dom):
        if u'id' in node.attrib and node.attrib[u'id'] in id_to_dom_node:
            target_dom_to_source_dom[id_to_dom_node[node.attrib[u'id']]] = node
        return target_dom_to_source_dom
    
    return reduce_dom_tree(map_target_dom_to_source_dom_aux, source_dom_node, {})

def compose_mappings(left, right):
    """Given two mappings left: A -> B and right: B -> C, create a
    hash result_map: A -> C. Only values in left (i.e. things from B)
    which have corresponding keys in right will have their keys mapped
    to values in right. """
    result_map = {}
    for left_key, left_val in left.iteritems():
        try:
            result_map[left_key] = right[left_val]
        except KeyError:
            pass
    return result_map

def _build_target_dom_to_doc_dom(unit_node, source_dom, target_dom):
    source_dom_to_doc_dom    = _map_source_dom_to_doc_dom(unit_node, source_dom)
    target_dom_to_source_dom = _map_target_dom_to_source_dom(source_dom, target_dom)
    return compose_mappings(target_dom_to_source_dom, source_dom_to_doc_dom)

@accepts(etree._Element, {etree._Element: etree._Element})
def _get_translated_node(target_node, target_dom_to_doc_dom):
    dom_node = target_dom_to_doc_dom[target_node]
    dom_node.tail = target_node.tail
    return dom_node

@accepts(etree._Element, etree._Element, {etree._Element: etree._Element})
def _build_translated_dom(dom_node, target_node, target_dom_to_doc_dom):
    """
    
    """
    dom_node.text = target_node.text
    dom_node.extend(_get_translated_node(child, target_dom_to_doc_dom) for child in target_node 
                    if target_dom_to_doc_dom[child] is not None)
    for dom_child, target_child in zip(dom_node, target_node):
        _build_translated_dom(dom_child, target_child, target_dom_to_doc_dom)

@accepts(IsCallable())
def replace_dom_text(make_parse_state):
    """Return a function """
    
    @accepts(etree._Element, base.TranslationUnit)
    def action(dom_node, unit):
        """Use the unit's target (or source in the case where there is no translation)
        to update the text in the dom_node and at the tails of its children."""
        source_dom            = etree.fromstring(u'<source>%s</source>' % unicode(unit.source))
        target_dom            = etree.fromstring(u'<target>%s</target>' % unicode(unit.target or unit.source))
        unit_node             = find_translatable_dom_nodes(dom_node, make_parse_state())[0]        
        target_dom_to_doc_dom = _build_target_dom_to_doc_dom(unit_node, source_dom, target_dom)
        
        dom_node[:] = []
        _build_translated_dom(dom_node, target_dom, target_dom_to_doc_dom)

    return action
