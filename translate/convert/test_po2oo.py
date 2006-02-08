#!/usr/bin/env python

from translate.convert import po2oo
from translate.convert import oo2po
from translate.misc import wStringIO
from translate.storage import po
from translate.storage import oo
from py import test
import warnings

class TestPO2OO:
    def setup_method(self, method):
        warnings.resetwarnings()

    def teardown_method(self, method):
        warnings.resetwarnings()

    def po2oo(self, posource):
        """helper that converts po source to oo source without requiring files"""
        inputfile = wStringIO.StringIO(posource)
        inputpo = po.pofile(inputfile)
        convertor = po2oo.po2oo()
        outputoo = convertor.convertfile(inputpo)
        return outputoo

    def merge2oo(self, oosource, posource):
        """helper that merges po translations to oo source without requiring files"""
        inputfile = wStringIO.StringIO(posource)
        inputpo = po.pofile(inputfile)
        templatefile = wStringIO.StringIO(oosource)
        templateoo = oo.oofile(templatefile)
        convertor = po2oo.reoo(templateoo)
        outputoo = convertor.convertfile(inputpo)
        return outputoo

    def convertoo(self, posource, ootemplate):
        """helper to exercise the command line function"""
        inputfile = wStringIO.StringIO(posource)
        outputfile = wStringIO.StringIO()
        templatefile = wStringIO.StringIO(ootemplate)
        assert po2oo.convertoo(inputfile, outputfile, templatefile, targetlanguage="en-US", timestamp=0)
        return outputfile.getvalue()

    def roundtripstring(self, entitystring):
        oointro, oooutro = r'svx	source\dialog\numpages.src	0	string	RID_SVXPAGE_NUM_OPTIONS	STR_BULLET			0	en-US	', '				20050924 09:13:58' + '\r\n'
        oosource = oointro + entitystring + oooutro
        ooinputfile = wStringIO.StringIO(oosource)
        ooinputfile2 = wStringIO.StringIO(oosource)
        pooutputfile = wStringIO.StringIO()
        oo2po.convertoo(ooinputfile, pooutputfile, ooinputfile2)
        posource = pooutputfile.getvalue()
        poinputfile = wStringIO.StringIO(posource)
        ootemplatefile = wStringIO.StringIO(oosource)
        oooutputfile = wStringIO.StringIO()
        po2oo.convertoo(poinputfile, oooutputfile, ootemplatefile, targetlanguage="en-US")
        ooresult = oooutputfile.getvalue()
        print "original oo:\n", oosource, "po version:\n", posource, "output oo:\n", ooresult
        assert ooresult.startswith(oointro) and ooresult.endswith(oooutro)
        return ooresult[len(oointro):-len(oooutro)]

    def check_roundtrip(self, oosource):
        """Checks that the round-tripped string is the same as the original"""
        assert self.roundtripstring(oosource) == oosource

    def test_convertoo(self):
        """checks that the convertoo function is working"""
        oointro, oooutro = r'svx	source\dialog\numpages.src	0	string	RID_SVXPAGE_NUM_OPTIONS	STR_BULLET			0	en-US	', '				20050924 09:13:58' + '\r\n'
        posource = '''#: numpages.src#RID_SVXPAGE_NUM_OPTIONS.STR_BULLET.string.text\nmsgid "Simple String"\nmsgstr "Dimpled Ring"\n'''
        ootemplate = oointro + 'Simple String' + oooutro
        ooexpected = oointro + 'Dimpled Ring' + oooutro
        newoo = self.convertoo(posource, ootemplate)
        assert newoo == ooexpected

    def test_roundtrip_simple(self):
        """checks that simple strings make it through a oo->po->oo roundtrip"""
        self.check_roundtrip('Hello')
        self.check_roundtrip('"Hello"')
        self.check_roundtrip('"Hello Everybody"')

    def test_roundtrip_escape(self):
        """checks that escapes in strings make it through a oo->po->oo roundtrip"""
        self.check_roundtrip(r'"Simple Escape \ \n \\ \: \t "')
        self.check_roundtrip(r'"End Line Escape \"')

    def test_roundtrip_quotes(self):
        """checks that (escaped) quotes in strings make it through a oo->po->oo roundtrip"""
        self.check_roundtrip(r"""'Quote Escape "" '""")
        self.check_roundtrip(r'''"Single-Quote ' "''')
        self.check_roundtrip(r'''"Single-Quote Escape \' "''')
        self.check_roundtrip(r"""'Both Quotes "" '' '""")

