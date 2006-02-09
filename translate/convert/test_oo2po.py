#!/usr/bin/env python

from translate.convert import oo2po
from translate.convert import test_convert
from translate.misc import wStringIO
from translate.storage import po
from translate.storage import oo

class TestOO2PO:
    def oo2po(self, oosource, sourcelanguage='en-US', targetlanguage='af-ZA'):
        """helper that converts oo source to po source without requiring files"""
        inputoo = oo.oofile(oosource)
        convertor = oo2po.oo2po(sourcelanguage, targetlanguage)
        outputpo = convertor.convertfile(inputoo)
        return outputpo

    def singleelement(self, pofile):
        """checks that the pofile contains a single non-header element, and returns it"""
        assert len(pofile.poelements) == 2
        assert pofile.poelements[0].isheader()
        return pofile.poelements[1]

    def test_simpleentity(self):
        """checks that a simple oo entry converts properly to a po entry"""
        oosource = r'svx	source\dialog\numpages.src	0	string	RID_SVXPAGE_NUM_OPTIONS	STR_BULLET			0	en-US	Character				20050924 09:13:58'
        pofile = self.oo2po(oosource)
        poelement = self.singleelement(pofile)
        assert po.unquotefrompo(poelement.msgid) == "Character"
        assert po.unquotefrompo(poelement.msgstr) == ""

    def test_escapes(self):
        """checks that a simple oo entry converts escapes properly to a po entry"""
        oosource = r"wizards	source\formwizard\dbwizres.src	0	string	RID_DB_FORM_WIZARD_START + 19				0	en-US	Newline \n Newline Tab \t Tab CR \r CR				20050924 09:13:58"
        pofile = self.oo2po(oosource)
        poelement = self.singleelement(pofile)
        poelementsrc = str(poelement)
        assert r"Newline \n Newline" in poelementsrc
        assert r"Tab \t Tab" in poelementsrc
        assert r"CR \r CR" in poelementsrc

class TestOO2POCommand(test_convert.TestConvertCommand):
    """Tests running actual oo2po commands on files"""
    convertmodule = oo2po

    def test_help(self):
        """tests getting help"""
        help_string = test_convert.TestConvertCommand.test_help(self)
        assert "--source-language=LANG" in help_string

