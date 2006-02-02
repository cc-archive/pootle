#!/usr/bin/env python

from translate.convert import po2dtd
from translate.misc import wStringIO
from translate.storage import po
from translate.storage import dtd
from py import test
import warnings

class TestPO2DTD:
    def setup_method(self, method):
        warnings.resetwarnings()

    def teardown_method(self, method):
        warnings.resetwarnings()

    def po2dtd(self, posource):
        """helper that converts po source to dtd source without requiring files"""
        inputfile = wStringIO.StringIO(posource)
        inputpo = po.pofile(inputfile)
        convertor = po2dtd.po2dtd()
        outputdtd = convertor.convertfile(inputpo)
        return outputdtd

    def merge2dtd(self, dtdsource, posource):
        """helper that merges po translations to dtd source without requiring files"""
        inputfile = wStringIO.StringIO(posource)
        inputpo = po.pofile(inputfile)
        templatefile = wStringIO.StringIO(dtdsource)
        templatedtd = dtd.dtdfile(templatefile)
        convertor = po2dtd.redtd(templatedtd)
        outputdtd = convertor.convertfile(inputpo)
        return outputdtd

    def convertdtd(self, posource, dtdtemplate):
        """helper to exercise the command line function"""
        inputfile = wStringIO.StringIO(posource)
        outputfile = wStringIO.StringIO()
        templatefile = wStringIO.StringIO(dtdtemplate)
	assert po2dtd.convertdtd(inputfile, outputfile, templatefile)
	return outputfile.getvalue()

    def test_joinlines(self):
        """tests that po lines are joined seamlessly (bug 16)"""
        multilinepo = '''#: pref.menuPath\nmsgid ""\n"<span>Tools &gt; Options</"\n"span>"\nmsgstr ""\n'''
        dtdfile = self.po2dtd(multilinepo)
        dtdsource = str(dtdfile)
        assert "</span>" in dtdsource

    def test_escapedstr(self):
        """tests that \n in msgstr is escaped correctly in dtd"""
        multilinepo = '''#: pref.menuPath\nmsgid "Hello\\nEveryone"\nmsgstr "Good day\\nAll"\n'''
        dtdfile = self.po2dtd(multilinepo)
        dtdsource = str(dtdfile)
        assert "Good day\\nAll" in dtdsource

    def test_ampersandwarning(self):
        """tests that proper warnings are given if invalid ampersands occur"""
        simplestring = '''#: simple.warningtest\nmsgid "Simple String"\nmsgstr "Dimpled &Ring"\n'''
        warnings.simplefilter("error")
        assert test.raises(Warning, po2dtd.removeinvalidamps, "simple.warningtest", "Dimpled &Ring")

    def test_missingaccesskey(self):
        """tests that proper warnings are given if access key is missing"""
        simplepo = '''#: simple.label\n#: simple.accesskey\nmsgid "Simple &String"\nmsgstr "Dimpled Ring"\n'''
        simpledtd = '''<!ENTITY simple.label "Simple String">\n<!ENTITY simple.accesskey "S">'''
        warnings.simplefilter("error")
        assert test.raises(Warning, self.merge2dtd, simpledtd, simplepo)

    def test_ampersandfix(self):
        """tests that invalid ampersands are fixed in the dtd"""
        simplestring = '''#: simple.string\nmsgid "Simple String"\nmsgstr "Dimpled &Ring"\n'''
        dtdfile = self.po2dtd(simplestring)
        dtdsource = str(dtdfile)
        assert "Dimpled Ring" in dtdsource

    def test_retains_hashprefix(self):
        """tests that hash prefixes in the dtd are retained"""
        hashpo = '''#: lang.version\nmsgid "__MOZILLA_LOCALE_VERSION__"\nmsgstr "__MOZILLA_LOCALE_VERSION__"\n'''
        hashdtd = '#expand <!ENTITY lang.version "__MOZILLA_LOCALE_VERSION__">\n'
        dtdfile = self.merge2dtd(hashdtd, hashpo)
        regendtd = str(dtdfile)
        assert regendtd == hashdtd

    def test_convertdtd(self):
	"""checks that the convertdtd function is working"""
        posource = '''#: simple.label\n#: simple.accesskey\nmsgid "Simple &String"\nmsgstr "Dimpled &Ring"\n'''
        dtdtemplate = '''<!ENTITY simple.label "Simple String">\n<!ENTITY simple.accesskey "S">\n'''
	dtdexpected = '''<!ENTITY simple.label "Dimpled Ring">\n<!ENTITY simple.accesskey "R">\n'''
	newdtd = self.convertdtd(posource, dtdtemplate)
	print newdtd
	assert newdtd == dtdexpected

    def test_newlines_escapes(self):
	"""check that we can handle a \n in the PO file"""
        posource = '''#: simple.label\n#: simple.accesskey\nmsgid "A hard coded newline.\\n"\nmsgstr "Hart gekoeerde nuwe lyne\\n"\n'''
	dtdtemplate = '<!ENTITY  simple.label "A hard coded newline.\\n">\n'
	dtdexpected = '''<!ENTITY simple.label "Hart gekoeerde nuwe lyne\\n">\n'''
        dtdfile = self.merge2dtd(dtdtemplate, posource)
	print dtdfile
        assert str(dtdfile) == dtdexpected

