#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2006-2007 Zuza Software Foundation
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

"""An xliff file specifically suited for handling the po representation of 
xliff. """

from translate.storage import xliff
from translate.storage import lisa 
from translate.storage import poheader
from translate.misc.multistring import multistring
from translate.misc import ourdom
import xml
import re

def hasplurals(thing):
    if not isinstance(thing, multistring):
        return False
    return len(thing.strings) > 1

class PoXliffUnit(xliff.xliffunit):
    """A class to specifically handle the plural units created from a po file."""
    def __init__(self, source, document=None, empty=False):
        self.units = []
        if document:
            self.document = document
        else:
            self.document = ourdom.Document()
            
        if empty:
            return

        if not hasplurals(source):
            super(PoXliffUnit, self).__init__(source, self.document)
            return

        self.xmlelement = self.document.createElement("group")
        self.xmlelement.setAttribute("restype", "x-gettext-plurals")
        self.setsource(source)

    def __eq__(self, other):
        if isinstance(other, PoXliffUnit):
            if len(self.units) != len(other.units):
                return False
            if len(self.units) == 0:
                return True
            if not super(PoXliffUnit, self).__eq__(other):
                return False
            for i in range(len(self.units)-1):
                if not self.units[i+1] == other.units[i+1]:
                    return False
            return True
        if len(self.units) <= 1:
            if isinstance(other, lisa.LISAunit):
                return super(PoXliffUnit, self).__eq__(other)
            else:
                return self.source == other.source and self.target == other.target
        return False

    def setsource(self, source, sourcelang="en"):
#        TODO: consider changing from plural to singular, etc.
        if not hasplurals(source):
            super(PoXliffUnit, self).setsource(source, sourcelang)
        else:
            target = self.target
            for unit in self.units:
                try:
                    self.xmlelement.removeChild(unit.xmlelement)
                except xml.dom.NotFoundErr:
                    pass
            self.units = []
            for s in source.strings:
                self.units.append(xliff.xliffunit(s, self.document))
                self.xmlelement.appendChild(self.units[-1].xmlelement)
            self.target = target

    def getsource(self):
        strings = [super(PoXliffUnit, self).getsource()]
        strings.extend([unit.source for unit in self.units[1:]])
        return multistring(strings)
    source = property(getsource, setsource)
    
    def settarget(self, text, lang='xx', append=False):
        if self.gettarget() == text:
            return
        if not self.hasplural():
            super(PoXliffUnit, self).settarget(text, lang, append)
            return
        if not isinstance(text, multistring):
            text = multistring(text)
        source = self.source
        sourcel = len(source.strings)
        targetl = len(text.strings)
        if sourcel < targetl:
            sources = source.strings + [source.strings[-1]] * (targetl - sourcel)
            targets = text.strings
            id = self.getid()
            self.source = multistring(sources)
            self.setid(id)
        elif targetl < sourcel:
            targets = text.strings + [""] * (sourcel - targetl)
        else:
            targets = text.strings
        
        for i in range(len(self.units)):
            self.units[i].target = targets[i]

    def gettarget(self):
        if self.hasplural():
            strings = [unit.target for unit in self.units]
            if strings:
                return multistring(strings)
            else:
                return None
        else:
            return super(PoXliffUnit, self).gettarget()

    target = property(gettarget, settarget)

    def addnote(self, text, origin=None):
        """Add a note specifically in a "note" tag"""
        if isinstance(text, str):
            text = text.decode("utf-8")
        note = self.document.createElement("note")
        note.appendChild(self.document.createTextNode(text))
        if origin:
            note.setAttribute("from", origin)
        self.xmlelement.appendChild(note)
        for unit in self.units[1:]:
            unit.addnote(text, origin)

    def getnotes(self, origin=None):
        #NOTE: We support both <context> and <note> tags in xliff files for comments
        if origin == "translator":
            notes = super(PoXliffUnit, self).getnotes("translator")
            trancomments = self.gettranslatorcomments()
            if notes == trancomments or trancomments.find(notes) >= 0:
                notes = ""
            elif notes.find(trancomments) >= 0:
                trancomments = notes
                notes = ""
            trancomments = trancomments + notes
            return trancomments
        elif origin in ["programmer", "developer", "source code"]:
            devcomments = super(PoXliffUnit, self).getnotes("developer")
            autocomments = self.getautomaticcomments()
            if devcomments == autocomments or autocomments.find(devcomments) >= 0:
                devcomments = ""
            elif devcomments.find(autocomments) >= 0:
                autocomments = devcomments
                devcomments = ""
            return autocomments
        else:
            return super(PoXliffUnit, self).getnotes(origin)

    def markfuzzy(self, value=True):
        super(PoXliffUnit, self).markfuzzy(value)
        for unit in self.units[1:]:
            unit.markfuzzy(value)

    def marktranslated(self):
        super(PoXliffUnit, self).marktranslated()
        for unit in self.units[1:]:
            unit.marktranslated()

    def setid(self, id):
        self.xmlelement.setAttribute("id", id)
        if len(self.units) > 1:
            for i in range(len(self.units)):
                self.units[i].setid("%s[%d]" % (id, i))

    def getlocations(self):
        """Returns all the references (source locations)"""
        groups = self.getcontextgroups("po-reference")
        references = []
        for group in groups:
            sourcefile = ""
            linenumber = ""
            for (type,text) in group:
                if type == "sourcefile":
                    sourcefile = text
                elif type == "linenumber":
                    linenumber = text
            assert sourcefile
            if linenumber:
                sourcefile = sourcefile + ":" + linenumber
            references.append(sourcefile)
        return references

    def getautomaticcomments(self):
        """Returns the automatic comments (x-po-autocomment), which corresponds
        to the #. style po comments."""
        def hasautocomment((type, text)):
            return type == "x-po-autocomment"
        groups = self.getcontextgroups("po-entry")
        comments = []
        for group in groups:
            commentpairs = filter(hasautocomment, group)
            for (type,text) in commentpairs:
                comments.append(text)
        return "\n".join(comments)
    
    def gettranslatorcomments(self):       
        """Returns the translator comments (x-po-trancomment), which corresponds
        to the # style po comments."""
        def hastrancomment((type, text)):
            return type == "x-po-trancomment"
        groups = self.getcontextgroups("po-entry")
        comments = []
        for group in groups:
            commentpairs = filter(hastrancomment, group)
            for (type,text) in commentpairs:
                comments.append(text)
        return "\n".join(comments)

    def isheader(self):
        return "gettext-domain-header" in self.getrestype()

    def createfromxmlElement(cls, element, document):
        if element.tagName == "trans-unit":
            object = cls(None, document=document, empty=True)
            object.xmlelement = element
            return object
        assert element.tagName == "group"
        group = cls(None, document, empty=True)
        group.xmlelement = element
        units = element.getElementsByTagName("trans-unit")
        for unit in units:
            group.units.append(xliff.xliffunit.createfromxmlElement(unit, document))
        return group
    createfromxmlElement = classmethod(createfromxmlElement)

    def hasplural(self):
        return self.xmlelement.tagName == "group"


class PoXliffFile(xliff.xlifffile, poheader.poheader):
    """a file for the po variant of Xliff files"""
    UnitClass = PoXliffUnit
    def __init__(self, *args, **kwargs):
        if not "sourcelanguage" in kwargs:
            kwargs["sourcelanguage"] = "en-US"
        xliff.xlifffile.__init__(self, *args, **kwargs)

    def createfilenode(self, filename, sourcelanguage="en-US", datatype="po"):
        # Let's ignore the sourcelanguage parameter opting for the internal 
        # one. PO files will probably be one language
        return super(PoXliffFile, self).createfilenode(filename, sourcelanguage=self.sourcelanguage, datatype="po")

    def addheaderunit(self, target, filename):
        unit = self.addsourceunit(target, filename, True)
        unit.target = target
        unit.xmlelement.setAttribute("restype", "x-gettext-domain-header")
        unit.xmlelement.setAttribute("approved", "no")
        unit.xmlelement.setAttribute("xml:space", "preserve")
        return unit

    def addplural(self, source, target, filename, createifmissing=False):
        """This method should now be unnecessary, but is left for reference"""
        assert isinstance(source, multistring)
        if not isinstance(target, multistring):
            target = multistring(target)
        sourcel = len(source.strings)
        targetl = len(target.strings)
        if sourcel < targetl:
            sources = source.strings + [source.strings[-1]] * targetl - sourcel
            targets = target.strings
        else:
            sources = source.strings
            targets = target.strings
        self._messagenum += 1
        pluralnum = 0
        group = self.creategroup(filename, True, restype="x-gettext-plural")
        for (src, tgt) in zip(sources, targets):
            unit = self.UnitClass(src, self.document)
            unit.target = tgt
            unit.setid("%d[%d]" % (self._messagenum, pluralnum))
            pluralnum += 1
            group.appendChild(unit.xmlelement)
            self.units.append(unit)

        if pluralnum < sourcel:
            for string in sources[pluralnum:]:
                unit = self.UnitClass(src, self.document)
                unit.xmlelement.setAttribute("translate", "no")
                unit.setid("%d[%d]" % (self._messagenum, pluralnum))
                pluralnum += 1
                group.appendChild(unit.xmlelement)
                self.units.append(unit)
        
        return self.units[-pluralnum]

    def parse(self, xml):
        """Populates this object from the given xml string"""
        #TODO: Make more robust
        def ispluralgroup(node):
            """determines whether the xml node refers to a getttext plural"""
            return node.getAttribute("restype") == "x-gettext-plurals"
        
        def isnonpluralunit(node):
            """determindes whether the xml node contains a plural like id.
            
            We want to filter out all the plural nodes, except the very first
            one in each group.
            """
            return re.match(r"\d+\[[123456]\]$", node.getAttribute("id")) is None

        def pluralunits(pluralgroups):
            for pluralgroup in pluralgroups:
                yield self.UnitClass.createfromxmlElement(pluralgroup, self.document)
        
        self.filename = getattr(xml, 'name', '')
        if hasattr(xml, "read"):
            xmlsrc = xml.read()
            xml.close()
            xml = xmlsrc
        self.document = ourdom.parseString(xml)
        assert self.document.documentElement.tagName == self.rootNode
        self.initbody()
        groups = self.document.getElementsByTagName("group")
        pluralgroups = filter(ispluralgroup, groups)
        termEntries = self.document.getElementsByTagName(self.UnitClass.rootNode)
        if termEntries is None:
            return

        singularunits = filter(isnonpluralunit, termEntries)
        pluralunit_iter = pluralunits(pluralgroups)
        try:
            nextplural = pluralunit_iter.next()
        except StopIteration:
            nextplural = None

        for entry in singularunits:
            term = self.UnitClass.createfromxmlElement(entry, self.document)
            if nextplural and unicode(term.source) in nextplural.source.strings:
                self.units.append(nextplural)
                try:
                    nextplural = pluralunit_iter.next()
                except StopIteration, i:
                    nextplural = None
            else:
                self.units.append(term)

