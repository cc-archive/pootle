#!/usr/bin/env python

from translate.convert import pot2po
from translate.misc import wStringIO
from translate.storage import po
from py import test
import warnings

class TestPO2DTD:
    def setup_method(self, method):
        warnings.resetwarnings()

    def teardown_method(self, method):
        warnings.resetwarnings()

    def convertpot(self, potsource, posource=None):
        """helper that converts pot source to po source without requiring files"""
        potfile = wStringIO.StringIO(potsource)
        if posource:
          pofile = wStringIO.StringIO(posource)
        else:
          pofile = None
        pooutfile = wStringIO.StringIO()
        pot2po.convertpot(potfile, pooutfile, pofile)
        pooutfile.seek(0)
	return po.pofile(pooutfile.read())

    def singleelement(self, pofile):
        """checks that the pofile contains a single non-header element, and returns it"""
        assert len(pofile.poelements) == 2
        assert pofile.poelements[0].isheader()
        return pofile.poelements[1]

    def test_convertpot_blank(self):
        """checks that the convertpot function is working"""
        potsource = '''#: simple.label\n#: simple.accesskey\nmsgid "A &hard coded newline.\\n"\nmsgstr ""\n'''
        newpo = self.convertpot(potsource)
        assert str(self.singleelement(newpo)) == potsource

    def test_convertpot_merging(self):
        """checks that the convertpot function is working"""
        potsource = '''#: simple.label\n#: simple.accesskey\nmsgid "A &hard coded newline.\\n"\nmsgstr ""\n'''
        posource = '''#: simple.label\n#: simple.accesskey\nmsgid "A &hard coded newline.\\n"\nmsgstr "&Hart gekoeerde nuwe lyne\\n"\n'''
        newpo = self.convertpot(potsource, posource)
        assert str(self.singleelement(newpo)) == posource

