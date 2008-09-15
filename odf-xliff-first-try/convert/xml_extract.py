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

from xml.sax.handler import ContentHandler, feature_namespaces, feature_namespace_prefixes
from xml.sax import make_parser

#def top(stack):
#    return stack[-1]
#
#def push(stack, val):
#    stack.append(val)
#
#def pop(stack):
#    return stack.pop()
#
#class XPathBreadcrumb(object):
#    def __init__(self):
#        self._xpath = []
#        self._tagtally = [{}]
#        
#    def start_tag(self, tagname):
#        tally_dict = top(self._tagtally)
#        tally = tally_dict.get(tagname, -1) + 1
#        tally_dict[tagname] = tally
#        push(self._xpath, (tagname, tally))
#        push(self._tagtally, {})
#      
#    def end_tag(self, tagname):
#        pop(self._xpath)
#        pop(self._tagtally)
#
#    def _get_xpath(self):
#        def str_component(component):
#            taginfo, pos = component
#            namespace, tagname = taginfo
#            return "%s[%d]" % (tagname, pos)
#      
#        return "/".join(str_component(component) for component in self._xpath)
#    
#    xpath = property(_get_xpath)
#
#class XMLExtractor(ContentHandler):
#    def __init__(self, namespace_table):
#        # Set ContentHandler properties
#        # Our own members
#        self._namespace_table = namespace_table
#        self._xpath_breadcrumb = XPathBreadcrumb()
#        self._char_stack = [[]]
#        
#    def startElementNS(self, name, qname, attrs):
#        self._xpath_breadcrumb.start_tag(name)
#        push(self._char_stack, [])
#
#    def endElementNS(self, name, qname):
#        content = pop(self._char_stack)
#        if qname in self._namespace_table:
#            self._namespace_table[qname](name, qname, None, self._xpath_breadcrumb.xpath, content)
#        top(self._char_stack).extend(content)
#        self._xpath_breadcrumb.end_tag(name)
#
#    def characters(self, content):
#        top(self._char_stack).append(content)
#
#
#def tag_stream(file):
#    extractor = Extractor()
#    parser = make_parser()
#    parser.setContentHandler(extractor)
#    parser.setFeature(feature_namespaces, True)
#    parser.parse(file)
#    file.close()
#    for element in extractor.stream:
#        yield element
#
#def make_extractor(namespace_table):
#    extractor = XMLExtractor(namespace_table)
#    xml_extractor = make_parser()
#    xml_extractor.setFeature(feature_namespaces, True)
#    #xml_extractor.setFeature(feature_namespace_prefixes, True)
#    xml_extractor.setContentHandler(extractor)
#    return xml_extractor

import re
import record
pattern = re.compile("{(?P<uri>[^}]+)}(?P<tag>.+)")

def push(lst, val):
    return (val, lst)
  
def head(lst):
    return lst[0]

def tail(lst):
    return lst[1]

def is_nil(tuple_list):
    return tuple_list is ()

def iter_tuple_list(tuple_list):
    if not is_nil(tuple_list):
        head, tail = tuple_list
        yield head
        while not is_nil(tail):
            head, tail = tail
            yield head

class ApplyState(record.Record("namespace_table", 
                               "source", 
                               "placable_id", 
                               "placable_name", 
                               "prev", 
                               "placables", 
                               "level", 
                               "xpath",
                               "text")):
    def prepare(cls, namespace_table):
        return (namespace_table, None, 0, None, None, None, 0, (), None)
    prepare=classmethod(prepare)

def add_translation(state, source):
    return state.setTranslations((source, state.translations))

def parse_tag(tag):
    match = pattern.match(tag)
    vals = match.groupdict()
    return vals['uri'], vals['tag']

def _get_text(node):
    yield (node.text or u"").strip()
    for child in node:
        yield (child.tail or u"").strip()

def get_text(node):
    return list(_get_text(node))

def process_placables(node, state):
    return reduce(lambda state, child: apply(child, state.alter(text = child.tail or u"")), node, state)

def process_children(node, state):
    return reduce(lambda state, child: apply(child, state), node, state)

def process_translatable_tag(node, state):
    if state.level > 0: # We don't want to bump up placable_id values for elements at the root.
        state = state.alter(placable_id = state.placable_id + 1)
    placables   = None
    source      = node.text or u""
    placable_id = state.placable_id
    if len(node) > 0:
        child_state = state.alter(level=state.level+1, prev = None, placables = None, source = None)
        placables   = process_placables(node, child_state)
        placable_id = child_state.placable_id
    if placables or "".join(source):
        return state.alter(placables = placables, source = source, prev = state, placable_id = placable_id)
    else:
        return state.alter(placable_id = placable_id)

def apply(node, state):
    def do_apply(node, state):
        uri, tag = parse_tag(node.tag)
        if (uri, node.prefix) in state.namespace_table:
            tag_table = state.namespace_table[uri, node.prefix]
            if tag in tag_table:
#                _f = tag_table[tag]
                return process_translatable_tag(node, state)
        return process_children(node, state)

    result = do_apply(node, state.alter(xpath=push(state.xpath, node.tag)))
    return result.alter(xpath=tail(result.xpath))

def enumerate_list(lst, state, func):
    if lst.prev != None:
        new_state = enumerate_list(lst.prev, state, func)
        return func(lst, new_state)
    else:
        return state

def make_source(element):
    def print_placable(element, source):
        return source + (u"[[%s:%d]] %s" % (element.placable_name, element.placable_id, element.text))
    
    return enumerate_list(element.placables, element.source, print_placable)

def process_element(element, store):
    if element.placables != None:
        unit = store.UnitClass(make_source(element))
        if element.level > 0:
            unit.addlocation("%d" % element.placable_id)
        store.addunit(unit)
        return enumerate_list(element.placables, store, process_element)
    else:
        unit = store.UnitClass(element.source)
        if element.level > 0:
            unit.addlocation("%d" % element.placable_id)
        store.addunit(unit)
        return store

def extract(node, store, namespace_table, placable_table):
    lst = apply(node, ApplyState(namespace_table))
    store = enumerate_list(lst, store, process_element)

def generic_processor(source, state):
    print(source)
    print("-------------------------")
    return source, state
