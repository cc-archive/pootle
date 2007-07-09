#!/usr/bin/python
# -*- coding: utf-8 -*-
#Copyright (c) 2006 - 2007 by The WordForge Foundation
#                       www.wordforge.org
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
# 
# See the LICENSE file for more details. 
# 
# Developed by:
#       Hok Kakada (hokkakada@khmeros.info)
#       Keo Sophon (keosophon@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
#       Seth Chanratha (sethchanratha@khmeros.info)
#
# This module is working on Operator.

from PyQt4 import QtCore, QtGui
from translate.storage import factory
from translate.storage import po
from translate.misc import quote
from translate.storage import poheader
from translate.storage import xliff
import pootling.modules.World as World
from pootling.modules.Status import Status
from pootling.modules.pickleTM import pickleTM
import os, sys
from pootling import __version__


class Operator(QtCore.QObject):
    """
    Operates on the internal datastructure.
    The class loads and saves files and navigates in the data.
    Provides means for searching and filtering.
    
    @signal currentStatus(string): emitted with the new status message
    @signal newUnits(store.units): emitted with the new units
    @signal currentUnit(unit): emitted with the current unit
    @signal updateUnit(): emitted when the views should update the unitÂ´s data
    @signal toggleFirstLastUnit(atFirst, atLast): emitted to allow dis/enable of actions
    @signal filterChanged(filter, lenFilter): emitted when the filter was changed
    @signal readyForSave(False): emitted when a file was saved
    """
    
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.store = None
        self.currentUnitIndex = 0
        self.filteredList = []
        self.filter = None
        self.glossaryChanged = True
        self.autoLookupUnit = False
        self.termMatcher = None
        self.tmMatcher = None
        self.termCache = {} # for improve glossary search speed
        self.tmCache = {} # for improve TM search speed

    def getUnits(self, fileName):
        """
        Read a file into the internal datastructure.
        @param fileName: the file to open, either a string or a file object.
        @return True of False indicates success open of file.
        """
        if (not os.path.exists(fileName)):
            QtGui.QMessageBox.critical(None, 'Error', fileName  + '\n' + 'The file doesn\'t exist.')
            return False
        try:
            store = factory.getobject(fileName)
        except Exception, e:
            QtGui.QMessageBox.critical(None, 'Error', 'Error while trying to read file ' + fileName  + '\n' + str(e))
            return False
        self.setNewStore(store)
        self.fileName = fileName
        return True
      
    def setNewStore(self, store):
        """
        Setup the oparator with a new storage.
        @param store: the new storage class.
        """
        self.store = store
        # filter flags
        self.filter = World.filterAll
        # get status for units
        self.status = Status(self.store)
        self.emitStatus()
        
        self.filteredList = []
        self.currentUnitIndex = 0
        for unit in self.store.units:
            # set x_editor_state for all units.
            if (unit.source == None):
                continue
            unit.x_editor_state = self.status.unitState(unit)
            if (self.filter & unit.x_editor_state):
                unit.x_editor_filterIndex = len(self.filteredList)
                self.filteredList.append(unit)
        self.emitNewUnits()
        self.setUnitFromPosition(0)
        self.setModified(False)

    def emitNewUnits(self):
        """
        Emit "newUnits" signal with a list of unit.
        """
        self.emit(QtCore.SIGNAL("newUnits"), self.filteredList)
        
    def emitStatus(self):
        """
        Emit "currentStatus" signal with a string contains total, fuzzy,
        translated, and untranslated messages of current file.
        """
        self.emit(QtCore.SIGNAL("currentStatus"), self.status.statusString())
    
    def emitUnit(self, unit):
        """
        Emit "currentUnit" signal with a unit.
        @param unit: class unit.
        """
        if (hasattr(unit, "x_editor_filterIndex")):
            self.currentUnitIndex = unit.x_editor_filterIndex
            self.searchPointer = unit.x_editor_filterIndex
        self.emit(QtCore.SIGNAL("currentUnit"), unit)
        
        self.emitLookupUnit()
        
    def getCurrentUnit(self):
        """
        @return the current unit.
        """
        if (self.currentUnitIndex < len(self.filteredList)):
            return self.filteredList[self.currentUnitIndex]
        else:
            return None
    
    def filterFuzzy(self, checked):
        """
        Add/remove fuzzy to filter, and send filter signal.
        @param checked: True or False when Fuzzy checkbox is checked or unchecked.
        """
        filter = self.filter
        if (checked):
            filter |= World.fuzzy
        elif (filter):
            filter &= ~World.fuzzy
        self.emitFiltered(filter)
    
    def filterTranslated(self, checked):
        """
        Add/remove translated to filter, and send filter signal.
        @param checked: True or False when Translated checkbox is checked or unchecked.
        """
        filter = self.filter
        if (checked):
            filter |= World.translated
        elif (filter):
            filter &= ~World.translated
        self.emitFiltered(filter)
    
    def filterUntranslated(self, checked):
        """
        Add/remove untranslated to filter, and send filter signal.
        @param checked: True or False when Untranslated checkbox is checked or unchecked.
        """
        filter = self.filter
        if (checked):
            filter |= World.untranslated
        elif (filter):
            filter &= ~World.untranslated
        self.emitFiltered(filter)
    
    def emitFiltered(self, filter):
        """
        Emit "filterChanged" signal with a filter and lenght of filtered list.
        """
        if (len(self.filteredList) > 0):
            unitBeforeFiltered = self.filteredList[self.currentUnitIndex]
        else:
            unitBeforeFiltered = None
        
        if (filter != self.filter):
            # build a new filteredList when only filter has changed.
            self.filter = filter
            self.filteredList = []
            for unit in self.store.units:
                if (self.filter & unit.x_editor_state):
                    unit.x_editor_filterIndex = len(self.filteredList)
                    self.filteredList.append(unit)
        self.emit(QtCore.SIGNAL("filterChanged"), filter, len(self.filteredList))
        if (unitBeforeFiltered) and (unitBeforeFiltered in self.filteredList):
            unit = unitBeforeFiltered
        elif (len(self.filteredList) > 0):
            unit = self.filteredList[0]
        else:
            unit = None
        self.emitUnit(unit)

    def headerData(self):
        """
        Get header info from the file.
        @return Header comment and Header dictonary.
        """
        if (not isinstance(self.store, poheader.poheader)):
            return (None, None)

        header = self.store.header() 
        if header:
            headerDic = self.store.parseheader()
            return (header.getnotes("translator"), headerDic)
        else:
            return ("", {})

    def makeNewHeader(self, headerDic):
        """
        Create a header with the information from headerDic.
        @param headerDic: a dictionary of arguments that are neccessary to form
        a header.
        @return: a dictionary with the header items.
        """

        if (hasattr(self.store, "x_generator")):
            self.store.x_generator = World.settingApp + ' ' + __version__.ver
        if isinstance(self.store, poheader.poheader):
            self.store.updateheader(add=True, **headerDic)
            self.setModified(True)
            return self.store.makeheaderdict(**headerDic)
        else: return {}
    
    def updateNewHeader(self, othercomments, headerDic):
        """
        Will update the existing header.
        @param othercomments: The comment of header file.
        @param headerDic: A header dictionary that has information about header.
        """
        #TODO: need to make it work with xliff file
        if (not isinstance(self.store, poheader.poheader)):
            return {}
        
        header = self.store.header()
        if (header):
            header.removenotes()
            header.addnote(unicode(othercomments))
            #TODO this code is also in the library po.py, so we should combine it.
            header.msgid = ['""']
            headeritems = self.store.makeheaderdict(**headerDic)
            header.msgstr = ['""']
            for (key, value) in headeritems.items():
                header.msgstr.append(quote.quotestr("%s: %s\\n" % (key, value)))
        self.setModified(True)

    def saveStoreToFile(self, fileName):
        """
        Save the temporary store into a file.
        @param fileName: String type.
        """
        if (World.settings.value("headerAuto", QtCore.QVariant(True)).toBool()):
            self.emit(QtCore.SIGNAL("headerAuto"))
        try:
            if (fileName):
                self.store.savefile(fileName)
            else:
                self.store.save()
            self.setModified(False)
        except Exception, e:
            QtGui.QMessageBox.critical(None, 
                                    'Error', 
                                    'Error while trying to write file ' 
                                    + fileName  + 
                                    '\n' + str(e))
    
    def setComment(self, comment, unit = None):
        """
        Set the comment to the unit or current unit.
        Call emitUnit() if unit is not current unit.
        @param comment: QString type.
        """
        if (self.currentUnitIndex < 0 or not self.filteredList):
            return
        newUnit = False
        if (not unit):
            unit = self.getCurrentUnit()
            newUnit = True
        unit.removenotes()
        unit.addnote(unicode(comment),'translator')
        if (newUnit):
            self.emitUnit(unit)
        self.setModified(True)
    
    def setTarget(self, target, unit = None):
        """
        Set the target to the unit or current unit.
        Call emitUnit() if unit is not current unit.
        @param target: Unicode sting type for single unit and list type for
        plural unit.
        """
        # if there is no translation unit in the view.
        if (self.currentUnitIndex < 0 or not self.filteredList):
            return
        newUnit = False
        if (not unit):
            unit = self.getCurrentUnit()
            newUnit = True
        # update target for current unit
        unit.settarget(target)
        #FIXME: this mark works single not plural unit.
        self.status.markTranslated(unit, (unit.target and True or False))
            
        if (newUnit):
            self.emitUnit(unit)
        self.emitStatus()
        self.setModified(True)
    
    def setUnitFromPosition(self, position):
        """
        Build a unit from position and call emitUnit().
        @param position: position inside the filtered list.
        """
        if (position < len(self.filteredList) and position >= 0):
            unit = self.filteredList[position]
            self.emitUnit(unit)

    def toggleFuzzy(self):
        """
        Toggle fuzzy state for current unit.
        """
        self.emit(QtCore.SIGNAL("requestTargetChanged"))
        if (self.currentUnitIndex < 0):
            return
        unit = self.getCurrentUnit()
        if (unit.x_editor_state & World.fuzzy):
            self.status.markFuzzy(unit, False)
        elif (unit.x_editor_state & World.translated):
            self.status.markFuzzy(unit, True)
        else:
            return
        self.emitUnit(unit)
        self.emitStatus()
        self.setModified(True)
    
    def initSearch(self, searchString, searchableText, matchCase):
        """
        Initilize the needed variables for searching.
        @param searchString: string to search for.
        @param searchableText: text fields to search through.
        @param matchCase: bool indicates case sensitive condition.
        """
        self.currentTextField = 0
        self.foundPosition = -1
        self.searchString = unicode(searchString)
        self.searchableText = searchableText
        self.matchCase = matchCase
        if (not matchCase):
            self.searchString = self.searchString.lower()

    def searchNext(self):
        """
        Search forward through the text fields.
        """
        if (not hasattr(self, "searchPointer")) or \
            (not hasattr(self, "searchableText")):
            return
        oldSearchPointer = self.searchPointer
        while (self.searchPointer < len(self.filteredList)):
            unitString = self._getUnitString()
            self.foundPosition = unitString.find(self.searchString, self.foundPosition + 1)
            # found in current textField
            if (self.foundPosition >= 0):
                self._searchFound()
                return True
                #break
            else:
                # next textField
                if (self.currentTextField < len(self.searchableText) - 1):
                    self.currentTextField += 1
                    continue
                # next unit
                else:
                    self.currentTextField = 0
                    self.searchPointer += 1
        else:
            # exhausted
            self._searchNotFound()
            self.emit(QtCore.SIGNAL("EOF"), "Next")
            self.searchPointer = oldSearchPointer

    def searchPrevious(self):
        """
        Search backward through the text fields.
        """
        if (not hasattr(self, "searchPointer")):
            return
        while (self.searchPointer >= 0):
            unitString = self._getUnitString()
            self.foundPosition = unitString.rfind(self.searchString, 0, self.foundPosition)
            # found in current textField
            if (self.foundPosition >= 0):
                self._searchFound()
                break
            else:
                # previous textField
                if (self.currentTextField > 0):
                    self.currentTextField -= 1
                    unitString = self._getUnitString()
                    self.foundPosition = len(unitString)
                    continue
                # previous unit
                else:
                    self.currentTextField = len(self.searchableText) - 1
                    self.searchPointer -= 1
                unitString = self._getUnitString()
                self.foundPosition = len(unitString)
        else:
            # exhausted
            self._searchNotFound()
            self.emit(QtCore.SIGNAL("EOF"), "Previous")
    
    def replace(self, replacedText):
        """
        Replace the found text in the text fields.
        @param replacedText: text to replace.
        """
        self.foundPosition = -1
        if self.searchNext():
            textField = self.searchableText[self.currentTextField]
            self.emit(QtCore.SIGNAL("replaceText"), \
                textField, \
                self.foundPosition, \
                len(unicode(self.searchString)), \
                replacedText)
            self.searchNext()

    def replaceAll(self, replacedText):
        """
        Replace the found text in the text fields through out the units.
        @param replacedText: text to replace.
        """
        self.foundPosition = -1
        while self.searchNext():
            textField = self.searchableText[self.currentTextField]
            self.emit(QtCore.SIGNAL("replaceText"), \
                textField, \
                self.foundPosition, \
                len(unicode(self.searchString)), \
                replacedText)
        
    def _getUnitString(self):
        """
        @return: the string of current text field.
        """
        if (self.searchPointer >= len(self.filteredList) or self.searchPointer < 0):
            return ""
        textField = self.searchableText[self.currentTextField]
        if (textField == World.source):
            unitString = self.filteredList[self.searchPointer].source
        elif (textField == World.target):
            unitString = self.filteredList[self.searchPointer].target
        elif (textField == World.comment):
            unitString = self.filteredList[self.searchPointer].getnotes()
        else:
            unitString = ""
        if (not self.matchCase):
            unitString = unitString.lower()
        return unitString

    def _searchFound(self):
        """
        Emit "searchResult" signal with searchString, textField, and
        foundPosition.
        """
        self.setUnitFromPosition(self.searchPointer)
        textField = self.searchableText[self.currentTextField]
        self.emit(QtCore.SIGNAL("searchResult"), self.searchString, textField, self.foundPosition)
    
    def _searchNotFound(self):
        """
        Emit "searchResult" signal with searchString="", textField, and
        foundPosition... indicates result not found.
        """
        textField = self.searchableText[self.currentTextField]
        self.emit(QtCore.SIGNAL("searchResult"), "", textField, -1)
    
    def closeFile(self):
        self.store = None
        self.status = None
        self.filter = None
        self.filteredList = []
        self.emitNewUnits()
        self.emitUnit(None)
        
    def setMatcher(self, matcher, section):
        """
        Set matcher or termMatcher to new matcher.
        @param matcher: class matcher.
        @param section: string indicates TM or glossary.
        """
        if (section == "TM"):
            self.tmMatcher = matcher
            self.tmCache = {}
        else:
            self.termMatcher = matcher
            self.termCache = {}
            self.glossaryChanged = True
        self.applySettings()
    
    def lookupUnit(self, unit):
        """
        Lookup a unit translation memory.
        @param unit: class unit.
        @return candidates as list of units, or None on error.
        """
        if (not self.autoLookupUnit):
            return None
        # get tmMatcher from pickle
        if (not self.tmMatcher):
            World.settings.beginGroup("TM")
            pickleFile = World.settings.value("pickleFile").toString()
            World.settings.endGroup()
            if (pickleFile):
                p = pickleTM()
                self.tmMatcher = p.getMatcher(pickleFile)
        if (not self.tmMatcher):
            return None

        if (not unit):
            return None
        # ignore fuzzy is checked.
        if (unit.isfuzzy() and self.ignoreFuzzyStatus):
            return None
        # use cache to improve search speed within 20 units.
        if self.tmCache.has_key(unit.source):
            candidates = self.tmCache[unit.source]
        else:
            candidates = self.tmMatcher.matches(unit.source)
            self.tmCache[unit.source] = candidates
            if (len(self.tmCache) > 20 ): 
                self.tmCache.popitem()
        return candidates
    
    def lookupTerm(self, term):
        """
        Lookup a term in glossary.
        @param term: a word to lookup in termMatcher.
        @return candidates as list of units
        """
        if (not self.autoLookupTerm):
            return None
        # get termMatcher from pickle
        if (not self.termMatcher):
            World.settings.beginGroup("Glossary")
            pickleFile = World.settings.value("pickleFile").toString()
            World.settings.endGroup()
            if (pickleFile):
                p = pickleTM()
                self.termMatcher = p.getMatcher(pickleFile)
        if (not self.termMatcher):
            return None
        # emit "glossaryPattern" when glossary changed
        if (self.glossaryChanged) and (self.termMatcher):
            self.glossaryChanged = False
            pattern = []
            for unit in self.termMatcher.candidates.units:
                pattern.append(unit.source)
            self.emit(QtCore.SIGNAL("glossaryPattern"), pattern)
        if (not term):
            return None
        # use cache to improve glossary search speed within 20 terms.
        if self.termCache.has_key(term):
            candidates = self.termCache[term]
        else:
            candidates = self.termMatcher.matches(term)
            # remove not exact term from candidates
            for candidate in candidates:
                if (candidate.source.lower() != term.lower()):
                    candidates.remove(candidate)
            self.termCache[term] = candidates
            if (len(self.termCache) > 20 ): 
                self.termCache.popitem()
        return candidates
    
    def emitGlossaryCandidates(self, term):
        """
        @emit "glossaryCandidates" signal as list of units.
        """
        candidates = self.lookupTerm(term)
        self.emit(QtCore.SIGNAL("termCandidates"), candidates)
    
    def emitTermRequest(self, term):
        """
        @emit "termRequest" signal as list of units.
        """
        candidates = self.lookupTerm(term)
        self.emit(QtCore.SIGNAL("termRequest"), candidates)
    
    def emitLookupUnit(self):
        """
        Lookup current unit's translation.
        @emit "tmCandidates" signal as list of units.
        """
        if (not hasattr(self, "lookupForTable")):
            self.lookupForTable = False
        
        if (self.lookupForTable):
            unit = self.getCurrentUnit()
            candidates = self.lookupUnit(unit)
            self.emit(QtCore.SIGNAL("tmCandidates"), candidates)
        else:
            self.emit(QtCore.SIGNAL("tmCandidates"), None)
    
    def emitRequestUnit(self):
        """
        Lookup current unit's translation.
        @emit "tmRequest" signal as list of units.
        """
        unit = self.getCurrentUnit()
        candidates = self.lookupUnit(unit)
        self.emit(QtCore.SIGNAL("tmRequest"), candidates)
    
    def setTmLookup(self, bool):
        """
        Set whether to auto lookup the current unit, e.g. tmTable is not
        visible, so don't bother to lookup unit.
        """
        self.lookupForTable = bool
        # when tm table shown, it need to be filled.
        if (bool):
            self.emitLookupUnit()
    
    def autoTranslate(self):
        """
        Auto translate units.
        """
        # for autoTranslate all units
        for unit in self.store.units:
            # if ignore fuzzy strings is checked, ad units is fuzzy do nothing.
            if (unit.istranslated() or \
                (not unit.source) or \
                (unit.isfuzzy() and self.ignoreFuzzyStatus)):
                continue
            
            candidates = self.lookupUnit(unit)
            # no condidates continue searching in next TM
            if (not candidates):
                continue
            
            self.setModified(True)
            # get the best candidates for targets in overview
            unit.settarget(candidates[0].target)
            # in XLiff, it is possible to have alternatives translation
            # TODO: add source original language and target language attribute
            if (isinstance(self.store, xliff.xlifffile)):
                for i in range(1, len(candidates)):
                    unit.addalttrans(candidates[i].target)
            self.status.markTranslated(unit, True)
            self.status.markFuzzy(unit, True)
        
        self.emitNewUnits()
        self.emitStatus()
    
    def setModified(self, bool):
        self.modified = bool
        self.emit(QtCore.SIGNAL("contentModified"), self.modified)
    
    def isModified(self):
        return ((hasattr(self, "modified") and self.modified) or False)
    
    def slotFindUnit(self, source):
        """
        Find a unit that contain source then emit currentUnit.
        @param source: source string used to search for unit.
        """
        unit = self.store.findunit(source)
        if unit:
            self.emitUnit(unit)
    
    def applySettings(self):
        """
        Set TM and Glossary settings.
        """
        TMpreference = World.settings.value("TMpreference").toInt()[0]
        self.autoLookupUnit = (TMpreference & 1 and True or False)
        self.ignoreFuzzyStatus = (TMpreference & 2 and True or False)
        self.addTranslation = (TMpreference & 4 and True or False)
        self.maxLen = World.settings.value("max_string_len", QtCore.QVariant(70)).toInt()[0]
        self.emitLookupUnit()
        
        GlossaryPreference = World.settings.value("GlossaryPreference").toInt()[0]
        self.autoLookupTerm = (GlossaryPreference & 1 and True or False)
        self.ChangeTerm = (GlossaryPreference & 2 and True or False)
        self.DetectTerm = (GlossaryPreference & 8 and True or False)
        self.AddNewTerm = (GlossaryPreference & 16 and True or False)
        self.SuggestTranslation = (GlossaryPreference & 32 and True or False)
        
        # set pattern for glossary
        self.lookupTerm(None)
        self.emit(QtCore.SIGNAL("highlightGlossary"), self.autoLookupTerm)

