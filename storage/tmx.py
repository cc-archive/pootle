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

"""module for parsing TMX translation memeory files"""

from translate.storage import lisa

from xml.dom import minidom
from translate import __version__

class tmxunit(lisa.LISAunit):
    """A single unit in the TMX file."""
    rootNode = "tu"
    languageNode = "tuv"
    textNode = "seg"
                   
    def createlanguageNode(self, lang, text, purpose):
        """returns a langset xml Element setup with given parameters"""
        langset = self.document.createElement(self.languageNode)
        assert self.document == langset.ownerDocument
        langset.setAttribute("xml:lang", lang)
        seg = self.document.createElement(self.textNode)
        segtext = self.document.createTextNode(text)
        
        langset.appendChild(seg)
        seg.appendChild(segtext)
        return langset


class tmxfile(lisa.LISAfile):
    """Class representing a TMX file store."""
    UnitClass = tmxunit
    rootNode = "tmx"
    bodyNode = "body"
    XMLskeleton = '''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE tmx SYSTEM "tmx14.dtd">
<tmx version="1.4">
<header></header>
<body></body>
</tmx>'''
    
    def addheader(self):
        headernode = self.document.getElementsByTagName("header")[0]
        headernode.setAttribute("creationtool", "Translate Toolkit - po2tmx")
        headernode.setAttribute("creationtoolversion", __version__.ver)
        headernode.setAttribute("segtype", "sentence")
        headernode.setAttribute("o-tmf", "UTF-8")
        headernode.setAttribute("adminlang", "en")
        #TODO: consider adminlang. Used for notes, etc. Possibly same as targetlanguage
        headernode.setAttribute("srclang", self.sourcelanguage)
        headernode.setAttribute("datatype", "PlainText")
        #headernode.setAttribute("creationdate", "YYYYMMDDTHHMMSSZ"
        #headernode.setAttribute("creationid", "CodeSyntax"

    def addtranslation(self, source, srclang, translation, translang):
        """addtranslation method for testing old unit tests"""
        unit = self.addsourceunit(source)
        unit.target = translation
        unit.xmlelement.getElementsByTagName("tuv")[0].setAttribute("xml:lang", srclang)
        unit.xmlelement.getElementsByTagName("tuv")[1].setAttribute("xml:lang", translang)

    def translate(self, sourcetext, sourcelang=None, targetlang=None):
        """method to test old unit tests"""
        return getattr(self.findunit(sourcetext), "target", None)

