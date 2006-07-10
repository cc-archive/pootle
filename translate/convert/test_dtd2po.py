#!/usr/bin/env python

from translate.convert import dtd2po
from translate.convert import test_convert
from translate.misc import wStringIO
from translate.storage import po
from translate.storage import dtd

class TestDTD2PO:
    def dtd2po(self, dtdsource, dtdtemplate=None):
        """helper that converts dtd source to po source without requiring files"""
        inputfile = wStringIO.StringIO(dtdsource)
        inputdtd = dtd.dtdfile(inputfile)
        convertor = dtd2po.dtd2po()
        if not dtdtemplate:
          outputpo = convertor.convertfile(inputdtd)
        else:
          templatefile = wStringIO.StringIO(dtdtemplate)
          templatedtd = dtd.dtdfile(templatefile)
          outputpo = convertor.mergefiles(templatedtd, inputdtd)
        return outputpo

    def convertdtd(self, dtdsource):
        """call the convertdtd, return the outputfile"""
        inputfile = wStringIO.StringIO(dtdsource)
        outputfile = wStringIO.StringIO()
        templatefile = None
        assert dtd2po.convertdtd(inputfile, outputfile, templatefile)
        return outputfile.getvalue()

    def singleelement(self, pofile):
        """checks that the pofile contains a single non-header element, and returns it"""
        assert len(pofile.units) == 2
        assert pofile.units[0].isheader()
        return pofile.units[1]

    def countelements(self, pofile):
        """returns the number of non-header items"""
        if pofile.units[0].isheader():
          return len(pofile.units) - 1
        else:
          return len(pofile.units)

    def test_simpleentity(self):
        """checks that a simple dtd entity definition converts properly to a po entry"""
        dtdsource = '<!ENTITY test.me "bananas for sale">\n'
        pofile = self.dtd2po(dtdsource)
        pounit = self.singleelement(pofile)
        assert po.unquotefrompo(pounit.msgid) == "bananas for sale"
        assert po.unquotefrompo(pounit.msgstr) == ""
        # Now with a template language
        dtdtemplate = '<!ENTITY test.me "bananas for sale">\n'
        dtdtranslated = '<!ENTITY test.me "piesangs te koop">\n'
        pofile = self.dtd2po(dtdtranslated, dtdtemplate)
        pounit = self.singleelement(pofile)
        assert po.unquotefrompo(pounit.msgid) == "bananas for sale"
        assert po.unquotefrompo(pounit.msgstr) == "piesangs te koop"

    def test_convertdtd(self):
        """checks that the convertdtd function is working"""
        dtdsource = '<!ENTITY saveas.label "Save As...">\n'
        posource = self.convertdtd(dtdsource)
        pofile = po.pofile(wStringIO.StringIO(posource))
        unit = self.singleelement(pofile)
        assert po.unquotefrompo(unit.msgid) == "Save As..."
        assert po.unquotefrompo(unit.msgstr) == ""

    def test_apos(self):
        """apostrophe should not break a single-quoted entity definition, bug 69"""
        dtdsource = "<!ENTITY test.me 'bananas &apos; for sale'>\n"
        pofile = self.dtd2po(dtdsource)
        pounit = self.singleelement(pofile)
        assert po.unquotefrompo(pounit.msgid) == "bananas ' for sale"

    def test_quotes(self):
        """quotes should be handled in a single-quoted entity definition"""
        dtdsource = """<!ENTITY test.metoo '"Bananas" for sale'>\n"""
        pofile = self.dtd2po(dtdsource)
        pounit = self.singleelement(pofile)
        print str(pounit)
        assert po.unquotefrompo(pounit.msgid) == '"Bananas" for sale'

    def test_emptyentity(self):
        """checks that empty entity definitions survive into po file, bug 15"""
        dtdsource = '<!ENTITY credit.translation "">\n'
        pofile = self.dtd2po(dtdsource)
        pounit = self.singleelement(pofile)
        assert "credit.translation" in str(pounit)

    def test_emptyentity_translated(self):
        """checks that if we translate an empty entity it makes it into the PO, bug 101"""
        dtdtemplate = '<!ENTITY credit.translation "">\n'
        dtdsource = '<!ENTITY credit.translation "Translators Names">\n'
        pofile = self.dtd2po(dtdsource, dtdtemplate)
        unit = self.singleelement(pofile)
        print unit
        assert "credit.translation" in str(unit)
        assert po.unquotefrompo(unit.msgstr) == "Translators Names"

    def test_kdecomment_merge(self):
        """test that LOCALIZATION NOTES are added properly as KDE comments and merged with duplicate comments"""
        dtdtemplate = '<!--LOCALIZATION NOTE (%s): Edit box appears beside this label -->\n' + \
            '<!ENTITY %s "If publishing to a FTP site, enter the HTTP address to browse to:">\n'
        dtdsource = dtdtemplate % ("note1.label", "note1.label") + dtdtemplate % ("note2.label", "note2.label")
        pofile = self.dtd2po(dtdsource)
        pofile.units = pofile.units[1:]
        posource = str(pofile)
        print posource
        assert posource.count('"_:') <= len(pofile.units)

    def test_donttranslate_simple(self):
        """check that we handle DONT_TRANSLATE messages properly"""
        dtdsource = '''<!-- LOCALIZATION NOTE (region.Altitude): DONT_TRANSLATE -->
<!ENTITY region.Altitude "Very High">'''
        pofile = self.dtd2po(dtdsource)
        assert self.countelements(pofile) == 0
        dtdsource = '''<!-- LOCALIZATION NOTE (exampleOpenTag.label): DONT_TRANSLATE: they are text for HTML tagnames: "<i>" and "</i>" -->
<!ENTITY exampleOpenTag.label "&lt;i&gt;">'''
        pofile = self.dtd2po(dtdsource)
        assert self.countelements(pofile) == 0
        dtdsource = '''<!-- LOCALIZATION NOTE (serverDirectory.label): DONT_TRANSLATE "IMAP" -->
<!ENTITY imapAdvanced.label "Advanced IMAP Server Settings">'''
        pofile = self.dtd2po(dtdsource)
        assert self.countelements(pofile) == 1

    def test_donttranslate_label(self):
        """test strangeness when label entity is marked DONT_TRANSLATE and accesskey is not, bug 30"""
        dtdsource = '<!--LOCALIZATION NOTE (editorCheck.label): DONT_TRANSLATE -->\n' + \
            '<!ENTITY editorCheck.label "Composer">\n<!ENTITY editorCheck.accesskey "c">\n'
        pofile = self.dtd2po(dtdsource)
        posource = str(pofile)
        # we need to decided what we're going to do here - see the comments in bug 30
        # this tests the current implementation which is that the DONT_TRANSLATE string is removed, but the other remains
        assert 'editorCheck.label' not in posource
        assert 'editorCheck.accesskey' in posource

    def test_donttranslate_onlyentity(self):
        """if the entity is itself just another entity then it shouldn't appear in the output PO file"""
        dtdsource = '''<!-- LOCALIZATION NOTE (mainWindow.title): DONT_TRANSLATE -->
<!ENTITY mainWindow.title "&brandFullName;">'''
        pofile = self.dtd2po(dtdsource)
        assert self.countelements(pofile) == 0

    def test_donttranslate_commentedout(self):
        """check that we don't process messages in <!-- comments -->: bug 102"""
        dtdsource = '''<!-- commenting out until bug 38906 is fixed
<!ENTITY messagesHeader.label         "Messages"> -->'''
        pofile = self.dtd2po(dtdsource)
        assert self.countelements(pofile) == 0

    def test_spaces_at_start_of_dtd_lines(self):
        """test that pretty print spaces at the start of subsequent DTD element lines are removed from the PO file, bug 79"""
        # Space at the end of the line
        dtdsource = '<!ENTITY  noupdatesfound.intro "First line then \n' + \
          '                                          next lines.">\n'
        pofile = self.dtd2po(dtdsource)
        pounit = self.singleelement(pofile)
        # We still need to decide how we handle line line breaks in the DTD entities.  It seems that we should actually
        # drop the line break but this has not been implemented yet.
        assert po.unquotefrompo(pounit.msgid, True) == "First line then \nnext lines."
        # No space at the end of the line
        dtdsource = '<!ENTITY  noupdatesfound.intro "First line then\n' + \
          '                                          next lines.">\n'
        pofile = self.dtd2po(dtdsource)
        unit = self.singleelement(pofile)
        assert po.unquotefrompo(unit.msgid, True) == "First line then \nnext lines."

    def test_accesskeys_folding(self):
	"""test that we fold accesskeys into message strings"""
	dtdsource_template = '<!ENTITY  fileSaveAs.%s "Save As...">\n<!ENTITY  fileSaveAs.%s "S">\n'
        lang_template = '<!ENTITY  fileSaveAs.%s "Gcina ka...">\n<!ENTITY  fileSaveAs.%s "G">\n'
        for label in ("label", "title"):
          for accesskey in ("accesskey", "accessKey", "akey"):
            pofile = self.dtd2po(dtdsource_template % (label, accesskey))
            pounit = self.singleelement(pofile)
            assert pounit.source == "&Save As..."
            # Test with template (bug 155)
            pofile = self.dtd2po(lang_template % (label, accesskey), dtdsource_template % (label, accesskey))
            pounit = self.singleelement(pofile)
            assert pounit.source == "&Save As..."
            assert pounit.target == "&Gcina ka..."

    def test_accesskeys_mismatch(self):
        """check that we can handle accesskeys that don't match and thus can't be folded into the .label entry"""
	dtdsource = '<!ENTITY  fileSave.label "Save">\n' + \
           '<!ENTITY  fileSave.accesskey "z">\n'
        pofile = self.dtd2po(dtdsource)
        assert self.countelements(pofile) == 2

    def test_carriage_return_in_multiline_dtd(self):
        """test that we create nice PO files when we find a \r\n in a multiline DTD element"""
        dtdsource = '<!ENTITY  noupdatesfound.intro "First line then \r\n' + \
          '                                          next lines.">\n'
        pofile = self.dtd2po(dtdsource)
        unit = self.singleelement(pofile)
        assert po.unquotefrompo(unit.msgid, True) == "First line then \nnext lines."

    def test_preserving_spaces(self):
        """test that we preserve space that appear at the start of the first line of a DTD entity"""
        # Space before first character
        dtdsource = '<!ENTITY mainWindow.titlemodifiermenuseparator " - ">'
        pofile = self.dtd2po(dtdsource)
        unit = self.singleelement(pofile)
        assert po.unquotefrompo(unit.msgid) == " - "
        # Double line and spaces
        dtdsource = '<!ENTITY mainWindow.titlemodifiermenuseparator " - with a newline\n    and more text">'
        pofile = self.dtd2po(dtdsource)
        unit = self.singleelement(pofile)
        assert po.unquotefrompo(unit.msgid, True) == " - with a newline \nand more text"

    def test_escaping_newline_tabs(self):
        """test that we handle all kinds of newline permutations"""
        dtdsource = '<!ENTITY  noupdatesfound.intro "A hard coded newline.\\nAnd tab\\t and a \\r carriage return.">\n'
        converter = dtd2po.dtd2po()
        thedtd = dtd.dtdunit()
        thedtd.parse(dtdsource)
        thepo = po.pounit()
        converter.convertstrings(thedtd, thepo)
        print thedtd
        print thepo.msgid
        # \n in a dtd should also appear as \n in the PO file
        assert po.unquotefrompo(thepo.msgid) == r"A hard coded newline.\nAnd tab\t and a \r carriage return."

    def test_abandoned_accelerator(self):
        """test that when a language DTD has an accelerator but the template DTD does not that we abandon the accelerator"""
        dtdtemplate = '<!ENTITY test.label "Test">\n'
        dtdlanguage = '<!ENTITY test.label "Toets">\n<!ENTITY test.accesskey "T">\n'
        pofile = self.dtd2po(dtdlanguage, dtdtemplate)
        unit = self.singleelement(pofile)
        assert po.unquotefrompo(unit.msgid) == "Test"
        assert po.unquotefrompo(unit.msgstr) == "Toets"

    def test_unassociable_accelerator(self):
        """test to see that we can handle accelerator keys that cannot be associated correctly"""
        dtdsource ='<!ENTITY  managecerts.button "Manage Certificates...">\n<!ENTITY  managecerts.accesskey "M">'
        pofile = self.dtd2po(dtdsource)
        assert pofile.units[1].source == "Manage Certificates..."
        assert pofile.units[2].source == "M"
        pofile = self.dtd2po(dtdsource, dtdsource)
        assert pofile.units[1].target == "Manage Certificates..."
        assert pofile.units[2].target == "M"

    def test_changed_labels_and_accelerators(self):
        """test to ensure that when the template changes an entity name we can still manage the accelerators""" 
        dtdtemplate = '''<!ENTITY  managecerts.caption      "Manage Certificates">
<!ENTITY  managecerts.text         "Use the Certificate Manager to manage your personal certificates, as well as those of other people and certificate authorities.">
<!ENTITY  managecerts.button       "Manage Certificates...">
<!ENTITY  managecerts.accesskey    "M">'''
        dtdlanguage = '''<!ENTITY managecerts.label "ﺇﺩﺍﺭﺓ ﺎﻠﺸﻫﺍﺩﺎﺗ">
<!ENTITY managecerts.text "ﺎﺴﺘﺧﺪﻣ ﻡﺪﻳﺭ ﺎﻠﺸﻫﺍﺩﺎﺗ ﻹﺩﺍﺭﺓ ﺶﻫﺍﺩﺎﺘﻛ ﺎﻠﺸﺨﺼﻳﺓ، ﺏﺍﻺﺿﺎﻓﺓ ﻞﺘﻠﻛ ﺎﻠﺧﺎﺻﺓ ﺏﺍﻶﺧﺮﻴﻧ ﻭ ﺲﻠﻃﺎﺗ ﺎﻠﺸﻫﺍﺩﺎﺗ.">
<!ENTITY managecerts.button "ﺇﺩﺍﺭﺓ ﺎﻠﺸﻫﺍﺩﺎﺗ...">
<!ENTITY managecerts.accesskey "ﺩ">'''
        pofile = self.dtd2po(dtdlanguage, dtdtemplate)
        print pofile
        assert pofile.units[3].source == "Manage Certificates..."
        assert pofile.units[3].target == "ﺇﺩﺍﺭﺓ ﺎﻠﺸﻫﺍﺩﺎﺗ..."
        assert pofile.units[4].source == "M"
        assert pofile.units[4].target == "ﺩ"

    def test_accelerator_keys_not_in_sentence(self):
        """tests to ensure that we can manage accelerator keys that are not part of the transated sentence eg in Chinese"""
        dtdtemplate = '''<!ENTITY useAutoScroll.label             "Use autoscrolling">
<!ENTITY useAutoScroll.accesskey         "a">'''
        dtdlanguage = '''<!ENTITY useAutoScroll.label             "使用自動捲動(Autoscrolling)">
<!ENTITY useAutoScroll.accesskey         "a">'''
        pofile = self.dtd2po(dtdlanguage, dtdtemplate)
        print pofile
        assert pofile.units[1].target == "使用自動捲動(&Autoscrolling)"
        # We assume that accesskeys with no associated key should be done as follows "XXXX (&A)"
        # TODO - check that we can unfold this from PO -> DTD
        dtdlanguage = '''<!ENTITY useAutoScroll.label             "使用自動捲動">
<!ENTITY useAutoScroll.accesskey         "a">'''
        pofile = self.dtd2po(dtdlanguage, dtdtemplate)
        print pofile
        assert pofile.units[1].target == "使用自動捲動 (&A)"

    def test_exclude_entity_includes(self):
        """test that we don't turn an include into a translatable string"""
        dtdsource = '<!ENTITY % brandDTD SYSTEM "chrome://branding/locale/brand.dtd">'
        pofile = self.dtd2po(dtdsource)
        assert self.countelements(pofile) == 0

    def test_linewraps(self):
        """check that empty line wraps are not placed in po file"""
        dtdsource = '''<!ENTITY generic.longDesc "
<p>Test me.</p>
">'''
        pofile = self.dtd2po(dtdsource)
        pounit = self.singleelement(pofile)
        assert po.unquotefrompo(pounit.msgid, True) == "<p>Test me.</p>"

class TestDTD2POCommand(test_convert.TestConvertCommand, TestDTD2PO):
    """Tests running actual dtd2po commands on files"""
    convertmodule = dtd2po
    defaultoptions = {"progress": "none"}

    def test_help(self):
        """tests getting help"""
        options = test_convert.TestConvertCommand.test_help(self)
        options = self.help_check(options, "-P, --pot")
        options = self.help_check(options, "-tTEMPLATE, --template=TEMPLATE")
        options = self.help_check(options, "--duplicates=DUPLICATESTYLE", last=True)
