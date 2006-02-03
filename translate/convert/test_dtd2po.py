#!/usr/bin/env python

from translate.convert import dtd2po
from translate.misc import wStringIO
from translate.storage import po
from translate.storage import dtd

class TestDTD2PO:
    def dtd2po(self, dtdsource):
        """helper that converts dtd source to po source without requiring files"""
        inputfile = wStringIO.StringIO(dtdsource)
        inputdtd = dtd.dtdfile(inputfile)
        convertor = dtd2po.dtd2po()
        outputpo = convertor.convertfile(inputdtd)
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
        assert len(pofile.poelements) == 2
        assert pofile.poelements[0].isheader()
        return pofile.poelements[1]

    def countelements(self, pofile):
        """returns the number of non-header items"""
        if pofile.poelements[0].isheader():
          return len(pofile.poelements) - 1
        else:
          return len(pofile.poelements)

    def test_simpleentity(self):
        """checks that a simple dtd entity definition converts properly to a po entry"""
        dtdsource = '<!ENTITY test.me "bananas for sale">\n'
        pofile = self.dtd2po(dtdsource)
        poelement = self.singleelement(pofile)
        assert po.unquotefrompo(poelement.msgid) == "bananas for sale"
        assert po.unquotefrompo(poelement.msgstr) == ""

    def test_convertdtd(self):
        """checks that the convertdtd function is working"""
        dtdsource = '<!ENTITY saveas.label "Save As...">\n'
        posource = self.convertdtd(dtdsource)
        pofile = po.pofile(wStringIO.StringIO(posource))
        poelement = self.singleelement(pofile)
        assert po.unquotefrompo(poelement.msgid) == "Save As..."
        assert po.unquotefrompo(poelement.msgstr) == ""

    def test_apos(self):
        """apostrophe should not break a single-quoted entity definition, bug 69"""
        dtdsource = "<!ENTITY test.me 'bananas &apos; for sale'>\n"
        pofile = self.dtd2po(dtdsource)
        poelement = self.singleelement(pofile)
        assert po.unquotefrompo(poelement.msgid) == "bananas ' for sale"

    def test_emptyentity(self):
        """checks that empty entity definitions survive into po file, bug 15"""
        dtdsource = '<!ENTITY credit.translation "">\n'
        pofile = self.dtd2po(dtdsource)
        poelement = self.singleelement(pofile)
        assert "credit.translation" in str(poelement)

    def test_kdecomment_merge(self):
        """test that LOCALIZATION NOTES are added properly as KDE comments and merged with duplicate comments"""
        dtdtemplate = '<!--LOCALIZATION NOTE (%s): Edit box appears beside this label -->\n' + \
            '<!ENTITY %s "If publishing to a FTP site, enter the HTTP address to browse to:">\n'
        dtdsource = dtdtemplate % ("note1.label", "note1.label") + dtdtemplate % ("note2.label", "note2.label")
        pofile = self.dtd2po(dtdsource)
        pofile.poelements = pofile.poelements[1:]
        posource = str(pofile)
        print posource
        assert posource.count('"_:') <= len(pofile.poelements)

    def test_donttranslate_simple(self):
        """check that we handle DONT_TRANSLATE messages properly"""
        dtdsource = '''<!-- LOCALIZATION NOTE (region.Altitude): DONT_TRANSLATE -->
<!ENTITY region.Altitude "Very High">'''
        pofile = self.dtd2po(dtdsource)
        assert self.countelements(pofile) == 0

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

    def test_spaces_at_start_of_dtd_lines(self):
        """test that pretty print spaces at the start of subsequent DTD element lines are removed from the PO file, bug 79"""
	# Space at the end of the line
        dtdsource = '<!ENTITY  noupdatesfound.intro "First line then \n' + \
          '                                          next lines.">\n'
        pofile = self.dtd2po(dtdsource)
        poelement = self.singleelement(pofile)
        assert po.unquotefrompo(poelement.msgid) == "First line then \nnext lines."
	# No space at the end of the line
        dtdsource = '<!ENTITY  noupdatesfound.intro "First line then\n' + \
          '                                          next lines.">\n'
        pofile = self.dtd2po(dtdsource)
        poelement = self.singleelement(pofile)
        assert po.unquotefrompo(poelement.msgid) == "First line then \nnext lines."

    def test_preserving_spaces(self):
	"""test that we preserve space that appear at the start of the first line of a DTD entity"""
	# Space before first character
	dtdsource = '<!ENTITY mainWindow.titlemodifiermenuseparator " - ">'
        pofile = self.dtd2po(dtdsource)
        poelement = self.singleelement(pofile)
        assert po.unquotefrompo(poelement.msgid) == " - "
	# Double line and spaces
	dtdsource = '<!ENTITY mainWindow.titlemodifiermenuseparator " - with a newline\n    and more text">'
        pofile = self.dtd2po(dtdsource)
        poelement = self.singleelement(pofile)
        assert po.unquotefrompo(poelement.msgid) == " - with a newline \nand more text"

    def test_newline_escaping(self):
	"""test that we handle all kinds of newline permutations"""
	dtdsource = '<!ENTITY  noupdatesfound.intro "A hard coded newline.\\n">\n'
        pofile = self.dtd2po(dtdsource)
        poelement = self.singleelement(pofile)
	print dtdsource
	print poelement.msgid
	# \n in a dtd should also appear as \n in the PO file
        assert poelement.msgid == r"A hard coded newline.\n"

