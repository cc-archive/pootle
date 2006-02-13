#!/usr/bin/env python

from translate.tools import pomerge
from translate.storage import po
from translate.misc import wStringIO

class TestPOMerge:
    def mergepo(self, templatesource, inputsource):
        """merges the sources of the given po files and returns a new po file object"""
        templatefile = wStringIO.StringIO(templatesource)
        inputfile = wStringIO.StringIO(inputsource)
        outputfile = wStringIO.StringIO()
        assert pomerge.mergepo(inputfile, outputfile, templatefile)
        outputpostring = outputfile.getvalue()
        outputpofile = po.pofile(outputpostring)
        return outputpofile

    def countelements(self, pofile):
        """returns the number of non-header items"""
        if pofile.poelements[0].isheader():
          return len(pofile.poelements) - 1
        else:
          return len(pofile.poelements)

    def singleelement(self, pofile):
        """checks that the pofile contains a single non-header element, and returns it"""
        assert self.countelements(pofile) == 1
        return pofile.poelements[-1]

    def test_simplemerge(self):
        """checks that a simple po entry merges OK"""
        templatepo = '''#: simple.test\nmsgid "Simple String"\nmsgstr ""\n'''
        inputpo = '''#: simple.test\nmsgid "Simple String"\nmsgstr "Dimpled Ring"\n'''
        pofile = self.mergepo(templatepo, inputpo)
        poelement = self.singleelement(pofile)
        assert po.unquotefrompo(poelement.msgid) == "Simple String"
        assert po.unquotefrompo(poelement.msgstr) == "Dimpled Ring"

    def test_replacemerge(self):
        """checks that a simple po entry merges OK"""
        templatepo = '''#: simple.test\nmsgid "Simple String"\nmsgstr "Dimpled Ring"\n'''
        inputpo = '''#: simple.test\nmsgid "Simple String"\nmsgstr "Dimpled King"\n'''
        pofile = self.mergepo(templatepo, inputpo)
        poelement = self.singleelement(pofile)
        assert po.unquotefrompo(poelement.msgid) == "Simple String"
        assert po.unquotefrompo(poelement.msgstr) == "Dimpled King"

