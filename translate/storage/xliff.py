#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2002-2004 Zuza Software Foundation
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

"""module for parsing .xliff files for translation"""

from translate.storage import lisa
from xml.dom import minidom

def writexml(self, writer, indent="", addindent="", newl=""):
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

# commented out modifications to minidom classes
'''
Element_writexml = minidom.Element.writexml
for elementclassname in dir(minidom):
  elementclass = getattr(minidom, elementclassname)
  if not isinstance(elementclass, type(minidom.Element)):
    continue
  if not issubclass(elementclass, minidom.Element):
    continue
  if elementclass.writexml != Element_writexml:
    continue
  elementclass.writexml = writexml
'''

# TODO: handle translation types

class xliffunit(lisa.LISAunit):
    """A single term in the xliff file.""" 
    rootNode = "trans-unit"
    languageNode = "source"
    textNode = ""

    #TODO: id and all the trans-unit level stuff

    def createlanguageNode(self, lang, text, purpose):
        """returns an xml Element setup with given parameters"""
        #TODO: for now we do source, but we have to test if it is target, perhaps 
        # with parameter. Alternatively, we can use lang, if supplied, since an xliff 
        #file has to conform to the bilingual nature promised by the header.
        assert purpose
        langset = self.document.createElement(purpose)
        #TODO: check language
#        langset.setAttribute("xml:lang", lang)

#        message = self.document.createTextNode(text)
#        langset.appendChild(message)
        self.createPHnodes(langset, text)
        return langset
    
    def getlanguageNodes(self):
        """We override this to get source and target nodes."""
        return self.xmlelement.getElementsByTagName(self.languageNode) + \
                self.xmlelement.getElementsByTagName("target")

    def addnote(self, text, origin=None):
        """Add a note specifically in a "note" tag"""
        note = self.document.createElement("note")
        note.appendChild(self.document.createTextNode(text))
        if origin:
            note.setAttribute("from", origin)
        self.xmlelement.appendChild(note)        

    def getnotes(self):
        """Returns the text from all the notes"""
        return lisa.getText(self.xmlelement.getElementsByTagName("note"))

    def isapproved(self):
        return self.xmlelement.getAttribute("approved") == "yes"

    def isfuzzy(self):
        targetnode = self.getlanguageNode(lang=None, index=1)
        return not targetnode is None and \
                (targetnode.getAttribute("state-qualifier") == "fuzzy-match" or \
                targetnode.getAttribute("state") == "needs-review-translation")
                
    def markfuzzy(self, value=True):
        targetnode = self.getlanguageNode(lang=None, index=1)
        if targetnode:
            if value:
                targetnode.setAttribute("state", "needs-review-translation")
                targetnode.setAttribute("state-qualifier", "fuzzy-match")
            elif self.isfuzzy():                
                targetnode.removeAttribute("state")
                targetnode.removeAttribute("state-qualifier")
        elif value:
            #If there is no target, we can't really indicate fuzzyness, so we set
            #approved to "no", but we don't take it into account in isfuzzy()
            #TODO: review decision
            self.xmlelement.setAttribute("approved", "no")

    def marktranslated(self):
        targetnode = self.getlanguageNode(lang=None, index=1)
        if not targetnode:
            return
        if self.isfuzzy():
            #TODO: consider
            targetnode.removeAttribute("state-qualifier", "fuzzy-match")
        targetnode.setAttribute("state", "translated")

    def setid(self, id):
        self.xmlelement.setAttribute("id", id)

    def getid(self):
        return self.xmlelement.getAttribute("id")

    def createcontextgroup(self, name, contexts=None, purpose=None):
        """Add the context group to the trans-unit with contexts a list with
        (type, text) tuples describing each context."""
        assert contexts
        group = self.document.createElement("context-group")
        group.setAttribute("name", name)
        if purpose:
            group.setAttribute("purpose", purpose)
        for type, text in contexts:
            context = self.document.createElement("context")
            context.setAttribute("context-type", type)
            nodetext = self.document.createTextNode(text)
            context.appendChild(nodetext)
            group.appendChild(context)
        self.xmlelement.appendChild(group)

    def getcontextgroups(self, name):
        """Returns the contexts in the context groups with the specified name"""
        groups = []
        grouptags = self.xmlelement.getElementsByTagName("context-group")
        for group in grouptags:
            if group.getAttribute("name") == name:
                contexts = group.getElementsByTagName("context")
                pairs = []
                for context in contexts:
                    pairs.append((context.getAttribute("context-type"), lisa.getText(context)))
                groups.append(pairs) #not extend
        return groups
        
    def getrestype(self):
        """returns the restype attribute in the trans-unit tag"""
        return self.xmlelement.getAttribute("restype")


class xlifffile(lisa.LISAfile):
    """Class representing a XLIFF file store."""
    UnitClass = xliffunit
    rootNode = "xliff"
    bodyNode = "body"
    XMLskeleton = '''<?xml version="1.0" ?>
<xliff version='1.1' xmlns='urn:oasis:names:tc:xliff:document:1.1'>
 <file original='NoName' source-language='en' datatype='plaintext'>
  <body>
  </body>
 </file>
</xliff>'''

    def __init__(self,*args,**kwargs):
        lisa.LISAfile.__init__(self,*args,**kwargs)
        self._filename = "NoName"
        self._messagenum = 0

    def addheader(self):
        """Initialise the file header."""
        self.document.getElementsByTagName("file")[0].setAttribute("source-language", self.sourcelanguage)

    def createfilenode(self, filename, sourcelanguage=None, datatype='plaintext'):
        """creates a filenode with the given filename. All parameters are needed
        for XLIFF compliance."""
        self.removedefaultfile()
        if sourcelanguage is None:
            sourcelanguage = self.sourcelanguage
        filenode = self.document.createElement("file")
        filenode.setAttribute("original", filename)
        filenode.setAttribute("source-language", sourcelanguage)
        filenode.setAttribute("datatype", datatype)
        bodyNode = self.document.createElement(self.bodyNode)
        filenode.appendChild(bodyNode)
        return filenode

    def getfilename(self, filenode):
        """returns the name of the given file"""
        return filenode.getAttribute("original")

    def getfilenode(self, filename):
        """finds the filenode with the given name"""
        filenodes = self.document.getElementsByTagName("file")
        for filenode in filenodes:
            if self.getfilename(filenode) == filename:
                return filenode
        return None

    def removedefaultfile(self):
        """We want to remove the default file-tag as soon as possible if we 
        know if still present and empty."""
        filenodes = self.document.getElementsByTagName("file")
        if len(filenodes) > 1:
            for filenode in filenodes:
                if filenode.getAttribute("original") == "NoName" and \
                        not filenode.getElementsByTagName(self.UnitClass.rootNode):
                    self.document.documentElement.removeChild(filenode)
                break

    def getheadernode(self, filenode, createifmissing=False):
        """finds the header node for the given filenode"""
        headernodes = list(filenode.getElementsByTagName("header"))
        if headernodes:
            return headernodes[0]
        if not createifmissing:
            return None
        headernode = minidom.Element("header")
        filenode.appendChild(headernode)
        return headernode

    def getbodynode(self, filenode, createifmissing=False):
        """finds the body node for the given filenode"""
        bodynodes = list(filenode.getElementsByTagName("body"))
        if bodynodes:
            return bodynodes[0]
        if not createifmissing:
            return None
        bodynode = self.document.createElement("body")
        filenode.appendChild(bodynode)
        return bodynode

    def addsourceunit(self, source, filename="NoName", createifmissing=False):
        """adds the given trans-unit to the last used body node if the filename has changed it uses the slow method instead (will create the nodes required if asked). Returns success"""
        if self._filename != filename:
            if not self.switchfile(filename, createifmissing):
              return None
        unit = super(xlifffile, self).addsourceunit(source)
        self._messagenum += 1
        unit.setid("%d" % self._messagenum)
        unit.xmlelement.setAttribute("xml:space", "preserve")
        return unit

    def switchfile(self, filename, createifmissing=False):
        """adds the given trans-unit (will create the nodes required if asked). Returns success"""
        self._filename = filename
        filenode = self.getfilenode(filename)
        if filenode is None:
            if not createifmissing:
                return False
            filenode = self.createfilenode(filename)
            self.document.documentElement.appendChild(filenode)

        self.body = self.getbodynode(filenode, createifmissing=createifmissing)
        if self.body is None:
            return False
        self._messagenum = len(list(self.body.getElementsByTagName("trans-unit")))
        #TODO: was 0 based before - consider
    #    messagenum = len(self.units)
        #TODO: we want to number them consecutively inside a body/file tag
        #instead of globally in the whole XLIFF file, but using len(self.units)
        #will be much faster
        return True
    
    def creategroup(self, filename="NoName", createifmissing=False, restype=None):
        """adds a group tag into the specified file"""
        if self._filename != filename:
            if not self.switchfile(filename, createifmissing):
              return None
        group = self.document.createElement("group")
        if restype:
            group.setAttribute("restype", restype)
        self.body.appendChild(group)
        return group
        
    def __str__(self):
        self.removedefaultfile()
        return super(xlifffile, self).__str__()
