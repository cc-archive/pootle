#!/usr/bin/env python

from translate.convert import po2dtd
from translate.convert import dtd2po
from translate.convert import test_convert
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

    def roundtripstring(self, entitystring):
        dtdintro, dtdoutro = '<!ENTITY Test.RoundTrip ', '>\n'
        dtdsource = dtdintro + entitystring + dtdoutro
        dtdinputfile = wStringIO.StringIO(dtdsource)
        dtdinputfile2 = wStringIO.StringIO(dtdsource)
        pooutputfile = wStringIO.StringIO()
        dtd2po.convertdtd(dtdinputfile, pooutputfile, dtdinputfile2)
        posource = pooutputfile.getvalue()
        poinputfile = wStringIO.StringIO(posource)
        dtdtemplatefile = wStringIO.StringIO(dtdsource)
        dtdoutputfile = wStringIO.StringIO()
        po2dtd.convertdtd(poinputfile, dtdoutputfile, dtdtemplatefile)
        dtdresult = dtdoutputfile.getvalue()
        print "original dtd:\n", dtdsource, "po version:\n", posource, "output dtd:\n", dtdresult
        assert dtdresult.startswith(dtdintro) and dtdresult.endswith(dtdoutro)
        return dtdresult[len(dtdintro):-len(dtdoutro)]

    def check_roundtrip(self, dtdsource):
        """Checks that the round-tripped string is the same as the original"""
        assert self.roundtripstring(dtdsource) == dtdsource

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

    def test_accesskeycase(self):
        """tests that access keys come out with the same case as the original, regardless"""
        simplepo_template = '''#: simple.label\n#: simple.accesskey\nmsgid "Simple &%s"\nmsgstr "Dimpled &%s"\n'''
        simpledtd_template = '''<!ENTITY simple.label "Simple %s">\n<!ENTITY simple.accesskey "%s">'''
        # we test each combination of label case and accelerator case
        for srcword in ("String", "string"):
            for destword in ("Ring", "ring"):
                for srcaccel, destaccel in ("SR", "sr"):
                    simplepo = simplepo_template % (srcword, destword)
                    simpledtd = simpledtd_template % (srcword, srcaccel)
                    dtdfile = self.merge2dtd(simpledtd, simplepo)
                    dtdfile.makeindex()
                    accel = dtd.unquotefromdtd(dtdfile.index["simple.accesskey"].definition)
                    assert accel == destaccel

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

    def test_roundtrip_simple(self):
        """checks that simple strings make it through a dtd->po->dtd roundtrip"""
        self.check_roundtrip('"Hello"')
        self.check_roundtrip('"Hello Everybody"')

    def test_roundtrip_escape(self):
        """checks that escapes in strings make it through a dtd->po->dtd roundtrip"""
        self.check_roundtrip(r'"Simple Escape \ \n \\ \: \t \r "')
        self.check_roundtrip(r'"End Line Escape \"')

    def test_roundtrip_quotes(self):
        """checks that (escaped) quotes in strings make it through a dtd->po->dtd roundtrip"""
        self.check_roundtrip(r"""'Quote Escape "" '""")
        self.check_roundtrip(r'''"Single-Quote ' "''')
        self.check_roundtrip(r'''"Single-Quote Escape \' "''')
        # NOTE: if both quote marks are present, than ' is converted to &apos;
        self.check_roundtrip(r"""'Both Quotes "" &apos;&apos; '""")
        assert self.roundtripstring(r"""'Both Quotes "" '' '""") == r"""'Both Quotes "" &apos;&apos; '"""

    def test_merging_entries_with_spaces_removed(self):
        """dtd2po removes pretty printed spaces, this tests that we can merge this back into the pretty printed dtd"""
        posource = '''#: simple.label\nmsgid "First line then "\n"next lines."\nmsgstr "Eerste lyne en dan volgende lyne."\n'''
        dtdtemplate = '<!ENTITY simple.label "First line then\n' + \
          '                                          next lines.">\n'
        dtdexpected = '<!ENTITY simple.label "Eerste lyne en dan volgende lyne.">\n'
        dtdfile = self.merge2dtd(dtdtemplate, posource)
        print dtdfile
        assert str(dtdfile) == dtdexpected

class TestPO2DTDCommand(test_convert.TestConvertCommand, TestPO2DTD):
    """Tests running actual po2dtd commands on files"""
    convertmodule = po2dtd
    defaultoptions = {"progress": "none"}

