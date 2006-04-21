#!/usr/bin/env python

from translate.storage import xliff
from translate.storage import test_base
from translate.misc import wStringIO
from translate.misc.multistring import multistring

from py import test

class TestXLIFFUnit(test_base.TestTranslationUnit):
    UnitClass = xliff.xliffunit
   
class TestXLIFFfile(test_base.TestTranslationStore):
    StoreClass = xliff.xlifffile
    def test_basic(self):
        xlifffile = xliff.xlifffile()
        assert xlifffile.units == []
        xlifffile.addsourceunit("Bla")
        assert len(xlifffile.units) == 1
        newfile = xliff.xlifffile.parsestring(str(xlifffile))
        print str(xlifffile)
        assert len(newfile.units) == 1
        assert newfile.units[0].source == "Bla"
        assert newfile.findunit("Bla").source == "Bla"
        assert newfile.findunit("dit") is None

    def test_source(self):
        xlifffile = xliff.xlifffile()
        xliffunit = xlifffile.addsourceunit("Concept")
        xliffunit.source = "Term"
        newfile = xliff.xlifffile.parsestring(str(xlifffile))
        print str(xlifffile)
        assert newfile.findunit("Concept") is None
        assert newfile.findunit("Term") is not None
    
    def test_target(self):
        xlifffile = xliff.xlifffile()
        xliffunit = xlifffile.addsourceunit("Concept")
        xliffunit.target = "Konsep"
        newfile = xliff.xlifffile.parsestring(str(xlifffile))
        print str(xlifffile)
        assert newfile.findunit("Concept").target == "Konsep"

    def test_sourcelanguage(self):
        xlifffile = xliff.xlifffile(sourcelanguage="xh")
        xmltext = str(xlifffile)
        print xmltext
        assert xmltext.find('source-language="xh"')> 0  
        #TODO: test that it also works for new files.
            
    def test_notes(self):
        xlifffile = xliff.xlifffile()
        unit = xlifffile.addsourceunit("Concept")
        unit.addnote("Please buy bread")
        assert unit.getnotes() == "Please buy bread"
        notenodes = unit.xmlelement.getElementsByTagName("note")
        assert len(notenodes) == 1

        unit.addnote("Please buy milk", origin="Mom")
        notenodes = unit.xmlelement.getElementsByTagName("note")
        assert len(notenodes) == 2
        assert not notenodes[0].hasAttribute("from")
        assert notenodes[1].getAttribute("from") == "Mom"

    def test_fuzzy(self):
        xlifffile = xliff.xlifffile()
        unit = xlifffile.addsourceunit("Concept")
        unit.markfuzzy()
        assert not unit.isfuzzy() #No target yet
        unit.target = "Konsep"
        assert not unit.isfuzzy()
        unit.markfuzzy()
        assert unit.isfuzzy()
        unit.markfuzzy(False)
        assert not unit.isfuzzy()
        unit.markfuzzy(True)
        assert unit.isfuzzy()

        #If there is no target, we can't really indicate fuzzyness, so we set
        #approved to "no". If we want isfuzzy() to reflect that, the line can
        #be uncommented
        unit.target = None
        assert unit.target is None
        print unit
        unit.markfuzzy(True)
        assert unit.xmlelement.getAttribute("approved") == "no"
        #assert unit.isfuzzy()


