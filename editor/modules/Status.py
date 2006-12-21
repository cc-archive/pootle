#!/usr/bin/python
# -*- coding: utf8 -*-
# WordForge Translation Editor
# Copyright 2006 WordForge Foundation
#
# Version 0.1 (31 August 2006)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Developed by:
#       Hok Kakada (hokkakada@khmeros.info)
#       Keo Sophon (keosophon@khmeros.info)
#       San Titvirak (titvirak@khmeros.info)
#       Seth Chanratha (sethchanratha@khmeros.info)
# 
# This module stores status

from translate.tools import pocount
import modules.World as World

class Status:
    def __init__(self, units):
        self.numTotal = len(units)
        self.numFuzzy = len(pocount.fuzzymessages(units))
        self.numTranslated = len(pocount.translatedmessages(units))
        for unit in units:
            unit.x_editor_state = self.getStatus(unit)

    def markFuzzy(self, unit, fuzzy):
        if (unit.isfuzzy() == fuzzy):
            return
        unit.markfuzzy(fuzzy)
        if (fuzzy):
            self.numFuzzy += 1
            self.numTranslated -= 1
            unit.x_editor_state |= World.fuzzy
            unit.x_editor_state &= ~World.translated
        else:
            self.numFuzzy -= 1
            self.numTranslated += 1
            unit.x_editor_state &= ~World.fuzzy
            unit.x_editor_state |= World.translated

    def markTranslated(self, unit, translated):
        if (translated):
            if (unit.x_editor_state & World.translated):
                return
            self.numTranslated += 1
            if hasattr(unit, "marktranslated"):
                unit.marktranslated()
            unit.x_editor_state |= World.translated
            unit.x_editor_state &= ~World.untranslated
        else:
            if (unit.x_editor_state & World.untranslated):
                return
            self.numTranslated -= 1
            unit.x_editor_state &= ~World.translated
            unit.x_editor_state |= World.untranslated
        if (unit.isfuzzy()):
            unit.markfuzzy(False)
            self.numFuzzy -= 1
            unit.x_editor_state &= ~World.fuzzy

    def getStatus(self, unit):
        """return the unit's status flag."""
        unitState = 0
        if (unit.istranslated()):
            unitState |= World.translated
        elif (unit.isfuzzy()):
            unitState |= World.fuzzy
        else:
            unitState |= World.untranslated
        return unitState
        
    def statusString(self):
        """return string of total, fuzzy, translated, and untranslated messages."""
        self.numUntranslated = self.numTotal - (self.numTranslated + self.numFuzzy)
        return "Total: "+ str(self.numTotal) + \
                "  |  Fuzzy: " +  str(self.numFuzzy) + \
                "  |  Translated: " +  str(self.numTranslated) + \
                "  |  Untranslated: " + str(self.numUntranslated)

