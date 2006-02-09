#!/usr/bin/env python

from translate.storage import tbx
from translate.storage import test_base
from translate.misc import wStringIO

from py import test

class TestTBXUnit(test_base.TestTranslationUnit):
	UnitClass = tbx.tbxunit

class TestTBXfile(test_base.TestTranslationStore):
	StoreClass = tbx.tbxfile
	def test_basic(self):
		tbxfile = tbx.tbxfile()
		assert tbxfile.units == []
		tbxfile.addsourceunit("Bla")
		assert len(tbxfile.units) == 1
		newfile = tbx.tbxfile.parsestring(str(tbxfile))
		print str(tbxfile)
		assert len(newfile.units) == 1
		assert newfile.units[0].source == "Bla"
		assert newfile.findunit("Bla").source == "Bla"
		assert test.raises(KeyError, newfile.findunit, "dit")

	def test_source(self):
		tbxfile = tbx.tbxfile()
		tbxunit = tbxfile.addsourceunit("Concept")
		tbxunit.source = "Term"
		newfile = tbx.tbxfile.parsestring(str(tbxfile))
		print str(tbxfile)
		assert test.raises(KeyError, newfile.findunit, "Concept")
		assert newfile.findunit("Term") is not None
	
	def test_target(self):
		tbxfile = tbx.tbxfile()
		tbxunit = tbxfile.addsourceunit("Concept")
		tbxunit.target = "Konsep"
		newfile = tbx.tbxfile.parsestring(str(tbxfile))
		print str(tbxfile)
		assert newfile.findunit("Concept").target == "Konsep"
		
