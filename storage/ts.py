#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2004-2006 Zuza Software Foundation
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

"""module for parsing Qt .ts files for translation"""

from xml.dom import minidom
from xml.dom import expatbuilder

# helper functions we use to do xml the way we want, used by modified classes below

# TODO: work out how to use writexml_helper if desired, otherwise remove it
def writexml_helper(self, writer, indent="", addindent="", newl=""):
    """a replacement to writexml that formats it more like typical .ts files"""
    # indent = current indentation
    # addindent = indentation to add to higher levels
    # newl = newline string
    writer.write(indent+"<" + self.tagName)

    attrs = self._get_attributes()
    a_names = attrs.keys()
    a_names.sort()

    for a_name in a_names:
        writer.write(" %s=\"" % a_name)
        minidom._write_data(writer, attrs[a_name].value)
        writer.write("\"")
    if self.childNodes:
        if len(self.childNodes) == 1 and self.childNodes[0].nodeType == self.TEXT_NODE:
          writer.write(">")
          for node in self.childNodes:
              node.writexml(writer,"","","")
          writer.write("</%s>%s" % (self.tagName,newl))
        else:
          writer.write(">%s"%(newl))
          for node in self.childNodes:
              node.writexml(writer,indent+addindent,addindent,newl)
          writer.write("%s</%s>%s" % (indent,self.tagName,newl))
    else:
        writer.write("/>%s"%(newl))

def getElementsByTagName_helper(parent, name, dummy=None):
    for node in parent.childNodes:
        if node.nodeType == minidom.Node.ELEMENT_NODE and \
            (name == "*" or node.tagName == name):
            yield node
        for othernode in node.getElementsByTagName(name):
            yield othernode

def searchElementsByTagName_helper(parent, name, onlysearch):
    """limits the search to within tags occuring in onlysearch"""
    for node in parent.childNodes:
        if node.nodeType == minidom.Node.ELEMENT_NODE and \
            (name == "*" or node.tagName == name):
            yield node
        if node.nodeType == minidom.Node.ELEMENT_NODE and node.tagName in onlysearch:
            for node in node.searchElementsByTagName(name, onlysearch):
                yield node

def getFirstElementByTagName(node, name):
  results = node.getElementsByTagName(name)
  if isinstance(results, list):
    return results[0]
  try:
    result = results.next()
    return result
  except StopIteration:
    return None

def getnodetext(node):
  """returns the node's text by iterating through the child nodes"""
  if node is None: return ""
  return "".join([t.data for t in node.childNodes if t.nodeType == t.TEXT_NODE])

# various modifications to minidom classes to add functionality we like

class DOMImplementation(minidom.DOMImplementation):
  def _create_document(self):
    return Document()

class Element(minidom.Element):
  def getElementsByTagName(self, name):
    return getElementsByTagName_helper(self, name)
  def searchElementsByTagName(self, name, onlysearch):
    return searchElementsByTagName_helper(self, name, onlysearch)
class Document(minidom.Document):
  implementation = DOMImplementation()
  def getElementsByTagName(self, name):
    return getElementsByTagName_helper(self, name)
  def searchElementsByTagName(self, name, onlysearch):
    return searchElementsByTagName_helper(self, name, onlysearch)
  def createElement(self, tagName):
    e = Element(tagName)
    e.ownerDocument = self
    return e
  def createElementNS(self, namespaceURI, qualifiedName):
    prefix, localName = _nssplit(qualifiedName)
    e = Element(qualifiedName, namespaceURI, prefix)
    e.ownerDocument = self
    return e

theDOMImplementation = DOMImplementation()

# an ExpatBuilder that allows us to use the above modifications

class ExpatBuilderNS(expatbuilder.ExpatBuilderNS):
  def reset(self):
    """Free all data structures used during DOM construction."""
    self.document = theDOMImplementation.createDocument(
      expatbuilder.EMPTY_NAMESPACE, None, None)
    self.curNode = self.document
    self._elem_info = self.document._elem_info
    self._cdata = False
    self._initNamespaces()

  def start_element_handler(self, name, attributes):
    # all we want to do is construct our own Element instead of minidom.Element
    # unfortunately the only way to do this is to copy this whole function from expatbuilder.py
    if ' ' in name:
      uri, localname, prefix, qname = _parse_ns_name(self, name)
    else:
      uri = expatbuilder.EMPTY_NAMESPACE
      qname = name
      localname = None
      prefix = expatbuilder.EMPTY_PREFIX
    node = Element(qname, uri, prefix, localname)
    node.ownerDocument = self.document
    expatbuilder._append_child(self.curNode, node)
    self.curNode = node

    if self._ns_ordered_prefixes:
      for prefix, uri in self._ns_ordered_prefixes:
        if prefix:
          a = minidom.Attr(_intern(self, 'xmlns:' + prefix),
                   expatbuilder.XMLNS_NAMESPACE, prefix, "xmlns")
        else:
          a = minidom.Attr("xmlns", expatbuilder.XMLNS_NAMESPACE,
                   "xmlns", expatbuilder.EMPTY_PREFIX)
        d = a.childNodes[0].__dict__
        d['data'] = d['nodeValue'] = uri
        d = a.__dict__
        d['value'] = d['nodeValue'] = uri
        d['ownerDocument'] = self.document
        _set_attribute_node(node, a)
      del self._ns_ordered_prefixes[:]

    if attributes:
      _attrs = node._attrs
      _attrsNS = node._attrsNS
      for i in range(0, len(attributes), 2):
        aname = attributes[i]
        value = attributes[i+1]
        if ' ' in aname:
          uri, localname, prefix, qname = _parse_ns_name(self, aname)
          a = minidom.Attr(qname, uri, localname, prefix)
          _attrs[qname] = a
          _attrsNS[(uri, localname)] = a
        else:
          a = minidom.Attr(aname, expatbuilder.EMPTY_NAMESPACE,
                   aname, expatbuilder.EMPTY_PREFIX)
          _attrs[aname] = a
          _attrsNS[(expatbuilder.EMPTY_NAMESPACE, aname)] = a
        d = a.childNodes[0].__dict__
        d['data'] = d['nodeValue'] = value
        d = a.__dict__
        d['ownerDocument'] = self.document
        d['value'] = d['nodeValue'] = value
        d['ownerElement'] = node

  if __debug__:
    # This only adds some asserts to the original
    # end_element_handler(), so we only define this when -O is not
    # used.  If changing one, be sure to check the other to see if
    # it needs to be changed as well.
    #
    def end_element_handler(self, name):
      curNode = self.curNode
      if ' ' in name:
        uri, localname, prefix, qname = _parse_ns_name(self, name)
        assert (curNode.namespaceURI == uri
            and curNode.localName == localname
            and curNode.prefix == prefix), \
            "element stack messed up! (namespace)"
      else:
        assert curNode.nodeName == name, \
             "element stack messed up - bad nodeName"
        assert curNode.namespaceURI == expatbuilder.EMPTY_NAMESPACE, \
             "element stack messed up - bad namespaceURI"
      self.curNode = curNode.parentNode
      self._finish_end_element(curNode)

# parser methods that use our modified xml classes

def parse(file, parser=None, bufsize=None):
  """Parse a file into a DOM by filename or file object."""
  builder = ExpatBuilderNS()
  if isinstance(file, basestring):
    fp = open(file, 'rb')
    try:
      result = builder.parseFile(fp)
    finally:
      fp.close()
  else:
    result = builder.parseFile(file)
  return result

def parseString(string, parser=None):
  """Parse a file into a DOM from a string."""
  builder = ExpatBuilderNS()
  return builder.parseString(string)

# The actual QtTsParser - the meat of this file

class QtTsParser:
  contextancestors = dict.fromkeys(["TS"])
  messageancestors = dict.fromkeys(["TS", "context"])
  def __init__(self, inputfile=None):
    """make a new QtTsParser, reading from the given inputfile if required"""
    self.filename = getattr(inputfile, "filename", None)
    self.knowncontextnodes = {}
    self.indexcontextnodes = {}
    if inputfile is None:
      self.document = parseString("<!DOCTYPE TS><TS></TS>")
    else:
      self.document = parse(inputfile)
      assert self.document.documentElement.tagName == "TS"

  def addtranslation(self, contextname, source, translation, comment=None, transtype=None, createifmissing=False):
    """adds the given translation (will create the nodes required if asked). Returns success"""
    contextnode = self.getcontextnode(contextname)
    if contextnode is None:
      if not createifmissing:
        return False
      # construct a context node with the given name
      contextnode = self.document.createElement("context")
      namenode = self.document.createElement("name")
      nametext = self.document.createTextNode(contextname)
      namenode.appendChild(nametext)
      contextnode.appendChild(namenode)
      self.document.documentElement.appendChild(contextnode)
    if contextname in self.indexcontextnodes:
      messagesourceindex = self.indexcontextnodes[contextname]
    else:
      messagesourceindex = {}
      for message in self.getmessagenodes(contextnode):
        messagesource = self.getmessagesource(message).strip()
        messagesourceindex[messagesource] = message
      self.indexcontextnodes[contextname] = messagesourceindex
    message = messagesourceindex.get(source.strip(), None)
    if message is not None:
      translationnode = getFirstElementByTagName(message, "translation")
      newtranslationnode = self.document.createElement("translation")
      translationtext = self.document.createTextNode(translation)
      newtranslationnode.appendChild(translationtext)
      message.replaceChild(newtranslationnode, translationnode)
      return True
    if not createifmissing:
      return False
    messagenode = self.document.createElement("message")
    sourcenode = self.document.createElement("source")
    sourcetext = self.document.createTextNode(source)
    sourcenode.appendChild(sourcetext)
    messagenode.appendChild(sourcenode)
    if comment:
        commentnode = self.document.createElement("comment")
        commenttext = self.document.createTextNode(comment)
        commentnode.appendChild(commenttext)
        messagenode.appendChild(commentnode)
    translationnode = self.document.createElement("translation")
    translationtext = self.document.createTextNode(translation)
    translationnode.appendChild(translationtext)
    if transtype:
      translationnode.setAttribute("type",transtype)
    messagenode.appendChild(translationnode)
    contextnode.appendChild(messagenode)
    messagesourceindex[source.strip()] = messagenode
    return True

  def getxml(self):
    """return the ts file as xml"""
    xml = self.document.toprettyxml(indent="    ", encoding="utf-8")
    xml = "\n".join([line for line in xml.split("\n") if line.strip()])
    return xml

  def getcontextname(self, contextnode):
    """returns the name of the given context"""
    namenode = getFirstElementByTagName(contextnode, "name")
    return getnodetext(namenode)

  def getcontextnode(self, contextname):
    """finds the contextnode with the given name"""
    contextnode = self.knowncontextnodes.get(contextname, None)
    if contextnode is not None:
      return contextnode
    contextnodes = self.document.searchElementsByTagName("context", self.contextancestors)
    for contextnode in contextnodes:
      if self.getcontextname(contextnode) == contextname:
        self.knowncontextnodes[contextname] = contextnode
        return contextnode
    return None

  def getmessagenodes(self, context=None):
    """returns all the messagenodes, limiting to the given context (name or node) if given"""
    if context is None:
      return self.document.searchElementsByTagName("message", self.messageancestors)
    else:
      if isinstance(context, (str, unicode)):
        # look up the context node by name
        context = self.getcontextnode(context)
        if context is None:
          return []
      return context.searchElementsByTagName("message", self.messageancestors)

  def getmessagesource(self, message):
    """returns the message source for a given node"""
    sourcenode = getFirstElementByTagName(message, "source")
    return getnodetext(sourcenode)

  def getmessagetranslation(self, message):
    """returns the message translation for a given node"""
    translationnode = getFirstElementByTagName(message, "translation")
    return getnodetext(translationnode)

  def getmessagetype(self, message):
    """returns the message translation attributes for a given node"""
    translationnode = getFirstElementByTagName(message, "translation")
    return translationnode.getAttribute("type")

  def getmessagecomment(self, message):
    """returns the message comment for a given node"""
    commentnode = getFirstElementByTagName(message, "comment")
    # NOTE: handles only one comment per msgid (OK)
    # and only one-line comments (can be VERY wrong) TODO!!!
    return getnodetext(commentnode)

  def iteritems(self):
    """iterates through (contextname, messages)"""
    for contextnode in self.document.searchElementsByTagName("context", self.contextancestors):
      yield self.getcontextname(contextnode), self.getmessagenodes(contextnode)

  def __del__(self):
    """clean up the document if required"""
    if hasattr(self, "document"):
      self.document.unlink()

