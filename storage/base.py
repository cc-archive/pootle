#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2006 Zuza Software Foundation
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

"""base classes for storage interfaces"""

import pickle

def force_override(method, baseclass):
    """forces derived classes to override method"""
    if type(method.im_self) == type(baseclass):
        # then this is a classmethod and im_self is the actual class
        actualclass = method.im_self
    else:
        actualclass = method.im_class
    if actualclass != baseclass:
        raise NotImplementedError("%s does not reimplement %s as required by %s" % (actualclass.__name__, method.__name__, baseclass.__name__))

class TranslationUnit(object):
    def __init__(self, source):
        """Constructs a TranslationUnit containing the given source string"""
        self.source = source
        self.target = None

    def __eq__(self, other):
        """Compares two TranslationUnits"""
        return self.source == other.source and self.target == other.target

    def settarget(self, target):
        """Sets the target string to the given value"""
        self.target = target

    def getlocations(self):
        """A list of source code locations. Shouldn't be implemented if the
        format doesn't support it."""
        return []
    
    def addlocation(self, locatin):
        """Add one location to the list of locations. Shouldn't be implemented
        if the format doesn't support it."""
        pass

    def addlocations(self, location):
        """Add a location or a list of locations. Most classes shouldn't need
        to implement this, but should rather implement addlocation()."""
        if isinstance(location, list):
            for item in location:
                self.addlocation(item)
        else:
            addlocation(location)

    def getnotes(self):
        """Returns all notes about this unit. It will probably be freeform text
        or something reasonable that can be synthesised by the format. It should
        not include location comments (see getlocations)"""
        return ""

    def addnote(self, text, origin=None):
        """Adds a note (comment). 
        Origin specifies who/where the comment comes from"""
        pass

    def isfuzzy(self):
        """Indicates whether this unit is fuzzy"""
        return False

    def hasplural(self):
        """Tells whether or not this specific unit has plural strings."""
        #TODO: Reconsider
        return False

    def merge(self, otherunit, overwrite=False, comments=True):
        """do basic format agnostic merging"""
        if self.target == "" or overwrite:
            self.target = otherunit.target

class TranslationStore(object):
    """Base class for stores for multiple translation units of type UnitClass"""
    UnitClass = TranslationUnit

    def __init__(self):
        """Constructs a blank TranslationStore"""
        self.units = []

    def addsourceunit(self, source):
        """Adds and returns a new unit with the given source string"""
        unit = self.UnitClass(source)
        self.units.append(unit)
        return unit

    def findunit(self, source):
        """Finds the unit with the given source string"""
        if len(getattr(self, "sourceindex", [])):
            return self.sourceindex[source]
        for unit in self.units:
            if unit.source == source:
                return unit
        return None

    def translate(self, source):
        unit = self.findunit(source)
        if unit and unit.target:
            return unit.target
        else:
            return None

    def makeindex(self):
        """Indexes the items in this store. At least .sourceindex should be usefull."""
        self.locationindex = {}
        self.sourceindex = {}
        for unit in self.units:
            self.sourceindex[unit.source] = unit
            if unit.hasplural():
                plural_source = unit.source.strings[1]
                self.sourceindex[plural_source] = unit
            for location in unit.getlocations():
                if location in self.locationindex:
                    # if sources aren't unique, don't use them
                    self.locationindex[location] = None
                else:
                    self.locationindex[location] = unit

    def __str__(self):
        """Converts to a string representation that can be parsed back using parse"""
        force_override(self.__str__, TranslationStore)
        return pickle.dumps(self)

    def parsestring(cls, storestring):
        """Converts the string representation back to an object"""
        force_override(cls.parsestring, TranslationStore)
        return pickle.loads(storestring)
    parsestring = classmethod(parsestring)

    def savefile(self, storefile):
        """Writes the string representation to the given file (or filename)"""
        storestring = str(self)
        if isinstance(storefile, basestring):
            storefile = open(storefile, "w")
        storefile.write(storestring)
        storefile.close()

    def parsefile(cls, storefile):
        """Reads the given file (or opens the given filename) and parses back to an object"""
        if isinstance(storefile, basestring):
            storefile = open(storefile, "r")
        if "r" in storefile.mode:
          storestring = storefile.read()
        else:
          storestring = ""
        return cls.parsestring(storestring)
    parsefile = classmethod(parsefile)

