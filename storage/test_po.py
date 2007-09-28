#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.storage import po
from translate.storage import test_base

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
