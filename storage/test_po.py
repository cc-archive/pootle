#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.storage import po
from translate.storage import test_base
from translate.misc import wStringIO

def test_roundtrip_quoting():
    specials = ['Fish & chips', 'five < six', 'six > five', 
                'Use &nbsp;', 'Use &amp;nbsp;' 
                'A "solution"', "skop 'n bal", '"""', "'''", 
                '\n', '\t', '\r', 
                '\\n', '\\t', '\\r', '\\"', '\r\n', '\\r\\n', '\\']
    for special in specials:
        quoted_special = po.quoteforpo(special)
        unquoted_special = po.unquotefrompo(quoted_special)
        print "special: %r\nquoted: %r\nunquoted: %r\n" % (special, quoted_special, unquoted_special)
        assert special == unquoted_special

class TestPOUnit(test_base.TestTranslationUnit):
    UnitClass = po.pounit

class TestPOFile(test_base.TestTranslationStore):
    StoreClass = po.pofile
    def poparse(self, posource):
        """helper that parses po source without requiring files"""
        dummyfile = wStringIO.StringIO(posource)
        pofile = self.StoreClass(dummyfile)
        return pofile

    def poregen(self, posource):
        """helper that converts po source to pofile object and back"""
        return str(self.poparse(posource))

    def pomerge(self, oldmessage, newmessage, authoritative):
        """helper that merges two messages"""
        dummyfile = wStringIO.StringIO(oldmessage)
        oldpofile = self.StoreClass(dummyfile)
        oldunit = oldpofile.units[0]
        dummyfile2 = wStringIO.StringIO(newmessage)
        if newmessage:
          newpofile = self.StoreClass(dummyfile2)
          newunit = newpofile.units[0]
        else:
          newunit = oldpofile.UnitClass()
        oldunit.merge(newunit, authoritative=authoritative)
        print oldunit
        return str(oldunit)

