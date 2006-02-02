#!/usr/bin/env python

from translate.convert import po2csv
from translate.misc import wStringIO
from translate.storage import po
from translate.storage import csvl10n

class TestPO2CSV:
    def po2csv(self, posource):
        """helper that converts po source to csv source without requiring files"""
        inputfile = wStringIO.StringIO(posource)
        inputpo = po.pofile(inputfile)
        convertor = po2csv.po2csv()
        outputcsv = convertor.convertfile(inputpo)
        return outputcsv

    def test_doublequote(self):
        """tests for imbedded double quotes"""
        minipo = r'''msgid "Hello \"All\""
msgstr "Hallo \"Almal\""'''
        csvfile = self.po2csv(minipo)
        element = csvfile.csvelements[0]
        assert element.msgid == 'Hello "All"'

