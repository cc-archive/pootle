#!/usr/bin/python
# -*- coding: utf8 -*-
# WordForge Translation Editor
# (c) 2006 Open Forum of Cambodia, all rights reserved.
#
# Version 1.0
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# See the LICENSE file for more details.
#
# Developed by:
#       Keo Sophon (keosophon@khmeros.info)about:blank
#

from PyQt4 import QtCore
from translate.storage import factory
##from modules.Status import Status

class status:
    def __init__(self, units):
        self.numFuzzy = 0
        self.numTranslated = 0
        self.numTotal = len(units)
        for i in range(self.numTotal):
            #count fuzzy TU
            if units[i].isfuzzy():
                self.numFuzzy += 1
            #cound translated TU
            if units[i].istranslated():
                self.numTranslated += 1                
        self.numUntranslated  = self.numTotal - self.numTranslated
        
    def status(self):
        return "Total: "+ str(self.numTotal) + "  |  Fuzzy: " +  str(self.numFuzzy) + "  |  Translated: " +  str(self.numTranslated) + "  |  Untranslated: " + str(self.numUntranslated)
        
    def addNumFuzzy(self):
        self.numFuzzy += 1

    def subNumFuzzy(self):
        self.numFuzzy -= 1

    def addNumTranslated(self):
        self.numTranslated += 1

    def addNumUntranslated(self):
        self.numUntranslated +=1
    
    def subNumUntranslated(self):
        self.numUntranslated -=1
        
    def subNumTranslated(self):
        self.numTranslated -= 1

class Operator(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.store = None
        self._modified = False
        self._saveDone = False
        
        self._unitpointer = None
        self.unitPointerList = []

    def getUnits(self, fileName):
        self.store = factory.getobject(fileName)
        
        self.unitStatus = status(self.store.units)
        self.emitNewUnits()
        self._unitpointer = 0
        self.emitCurrentUnit()
        self.emitCurrentStatus()

    def emitCurrentUnit(self):
        if (self._unitpointer == 0):
            self.firstUnit()
        elif (self._unitpointer == len(self.unitPointerList) - 1):
            self.lastUnit()
        else:
            self.middleUnit()
            
        currentUnit = self.unitPointerList[self._unitpointer]
        if (currentUnit != len(self.store.units)):
            self.emit(QtCore.SIGNAL("currentUnit"), self.store.units[currentUnit])
            self.emit(QtCore.SIGNAL("currentPosition"), self._unitpointer)

    def emitNewUnits(self):
        self._unitpointer = 0
        self.unitPointerList = range(len(self.store.units))
        self.emit(QtCore.SIGNAL("newUnits"), self.store.units)

    def emitFilteredUnits(self):
        numTotal = len(self.store.units)
        self._unitpointer = 0
        filteredUnits = []
        self.unitPointerList = []
        for i in range(numTotal):
            if (self.store.units[i].isfuzzy()):
                filteredUnits.append(self.store.units[i])
                self.unitPointerList.append(i)
        self.emit(QtCore.SIGNAL("newUnits"), filteredUnits)

    def emitUpdateUnit(self):
        if (self._unitpointer != None):            
            self.emit(QtCore.SIGNAL("updateUnit"))    
    
    def firstUnit(self):    
        self.emit(QtCore.SIGNAL("firstUnit"))
    
    def lastUnit(self):
        self.emit(QtCore.SIGNAL("lastUnit"))
    
    def middleUnit(self):
        self.emit(QtCore.SIGNAL("middleUnit"))
        
    def previous(self):
        if self._unitpointer > 0:
            self.emitUpdateUnit()
            self._unitpointer -= 1
            self.emitCurrentUnit()
        
    def next(self):
        # move to next unit inside the list, not the whole store.units
        if self._unitpointer < len(self.unitPointerList):
            self.emitUpdateUnit()
            #if (self._unitpointer == len(self.unitPointerList) - 1):
            #    self._unitpointer -= 1
            self._unitpointer += 1
            self.emitCurrentUnit()
        
    def first(self):
        self.emitUpdateUnit()
        self._unitpointer = 0
        self.emitCurrentUnit()
        
    def last(self):
        self.emitUpdateUnit()
        self._unitpointer = len(self.unitPointerList) - 1
        self.emitCurrentUnit()

    def saveStoreToFile(self, fileName):
        self.emitUpdateUnit()
        self.store.savefile(fileName)
        self._saveDone = True        

    def modified(self):
        self.emitUpdateUnit()
        if self._saveDone:
            self._modified = False
            self._saveDone = False
        return self._modified
    
    def setComment(self, comment):
        """set the comment which is QString type to the current unit."""
        currentUnit = self.unitPointerList[self._unitpointer]
        self.store.units[currentUnit].setnotes()
        self.store.units[currentUnit].addnote(unicode(comment))
        self._modified = True        
    
    def setTarget(self, target):
        """set the target which is QString type to the current unit."""
        unit = self.unitPointerList[self._unitpointer]
        currentUnit = self.store.units[unit]
        before_isuntranslated = not currentUnit.istranslated()
        currentUnit.target = unicode(target)
        if (currentUnit.target != ''):
            currentUnit.marktranslated()
        after_istranslated = currentUnit.istranslated()
        if (before_isuntranslated and after_istranslated):
            self.unitStatus.addNumTranslated()
            self.unitStatus.subNumUntranslated()
        elif (not before_isuntranslated and not after_istranslated):
            self.unitStatus.subNumTranslated()
            self.unitStatus.addNumUntranslated()
        self.emitCurrentStatus()
        self._modified = True                

    def setCurrentUnit(self, value):
        self.emitUpdateUnit()
        self._unitpointer = self.unitPointerList.index(value)
        self.emitCurrentUnit()

    def setCurrentPosition(self, value):
        self.emitUpdateUnit()
        self._unitpointer = value
        self.emitCurrentUnit()
    
    def toggleFuzzy(self):
        """toggle fuzzy state for current unit"""
        unit = self.unitPointerList[self._unitpointer]
        currentUnit = self.store.units[unit]
        fuzzy = not currentUnit.isfuzzy()
        currentUnit.markfuzzy(fuzzy)
        self._modified = True
        if (fuzzy):
            self.unitStatus.addNumFuzzy()
        else:
            self.unitStatus.subNumFuzzy()
        self.emitCurrentStatus()
    
    def emitCurrentStatus(self):    
        self.emit(QtCore.SIGNAL("currentStatus"), self.unitStatus.status())
    
    def cutEdit(self, object):        
        self.connect(object, QtCore.SIGNAL("copyAvailable(bool)"), QtCore.SLOT("setEnabled"))
        object.cut()
    
    def copyEdit(self, object):          
        self.connect(object, QtCore.SIGNAL("copyAvailable(bool)"), QtCore.SLOT("setEnabled"))
        object.copy()
        
    def undoEdit(self, object):
        object.document().undo()     
##        return self.connect(object, QtCore.SIGNAL("undoAvailable(bool)"), QtCore.SLOT("setEnabled"))
     
    def redoEdit(self, object):
        object.document().redo()

    
