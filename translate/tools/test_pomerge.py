#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.tools import pomerge
from translate.storage import po
from translate.storage import xliff 
from translate.misc import wStringIO

class TestPOMerge:
    xliffskeleton = '''<?xml version="1.0" ?>
<xliff version="1.1" xmlns="urn:oasis:names:tc:xliff:document:1.1">
  <file original="filename.po" source-language="en-US" datatype="po">
    <body>
        %s
    </body>
  </file>
</xliff>'''

    def mergepo(self, templatesource, inputsource):
        """merges the sources of the given files and returns a new pofile object"""
        templatefile = wStringIO.StringIO(templatesource)
        inputfile = wStringIO.StringIO(inputsource)
        outputfile = wStringIO.StringIO()
        assert pomerge.mergepo(inputfile, outputfile, templatefile)
        outputpostring = outputfile.getvalue()
        outputpofile = po.pofile(outputpostring)
        return outputpofile

    def mergexliff(self, templatesource, inputsource):
        """merges the sources of the given files and returns a new xlifffile object"""
        templatefile = wStringIO.StringIO(templatesource)
        inputfile = wStringIO.StringIO(inputsource)
        outputfile = wStringIO.StringIO()
        assert pomerge.mergexliff(inputfile, outputfile, templatefile)
        outputxliffstring = outputfile.getvalue()
        print "Generated XML:"
        print outputxliffstring
        outputxlifffile = xliff.xlifffile(outputxliffstring)
        return outputxlifffile

    def countunits(self, pofile):
        """returns the number of non-header items"""
        if pofile.units[0].isheader():
          return len(pofile.units) - 1
        else:
          return len(pofile.units)

    def singleunit(self, pofile):
        """checks that the pofile contains a single non-header unit, and returns it"""
        assert self.countunits(pofile) == 1
        return pofile.units[-1]

    def test_simplemerge(self):
        """checks that a simple po entry merges OK"""
        templatepo = '''#: simple.test\nmsgid "Simple String"\nmsgstr ""\n'''
        inputpo = '''#: simple.test\nmsgid "Simple String"\nmsgstr "Dimpled Ring"\n'''
        pofile = self.mergepo(templatepo, inputpo)
        pounit = self.singleunit(pofile)
        assert po.unquotefrompo(pounit.msgid) == "Simple String"
        assert po.unquotefrompo(pounit.msgstr) == "Dimpled Ring"

    def test_replacemerge(self):
        """checks that a simple po entry merges OK"""
        templatepo = '''#: simple.test\nmsgid "Simple String"\nmsgstr "Dimpled Ring"\n'''
        inputpo = '''#: simple.test\nmsgid "Simple String"\nmsgstr "Dimpled King"\n'''
        pofile = self.mergepo(templatepo, inputpo)
        pounit = self.singleunit(pofile)
        assert po.unquotefrompo(pounit.msgid) == "Simple String"
        assert po.unquotefrompo(pounit.msgstr) == "Dimpled King"

    def test_reflowed_source_comments(self):
        """ensure that we don't duplicate source comments (locations) if they have been reflowed"""
        templatepo = '''#: newMenu.label\n#: newMenu.accesskey\nmsgid "&New"\nmsgstr ""\n'''
        newpo = '''#: newMenu.label newMenu.accesskey\nmsgid "&New"\nmsgstr "&Nuwe"\n'''
        expectedpo = '''#: newMenu.label\n#: newMenu.accesskey\nmsgid "&New"\nmsgstr "&Nuwe"\n\n'''
        pofile = self.mergepo(templatepo, newpo)
        pounit = self.singleunit(pofile)
        print pofile
        assert pofile.getoutput() == expectedpo

    def test_merge_dont_delete_unassociated_comments(self):
        """ensure that we do not delete comments in the PO file that are not assocaited with a message block"""
        templatepo = '''# Lonely comment\n\n# Translation comment\nmsgid "Bob"\nmsgstr "Toolmaker"\n'''
        mergepo = '''# Translation comment\nmsgid "Bob"\nmsgstr "Builder"\n'''
        expectedpo = '''# Lonely comment\n\n# Translation comment\nmsgid "Bob"\nmsgstr "Builder"\n\n'''
        pofile = self.mergepo(templatepo, mergepo)
#        pounit = self.singleunit(pofile)
        print pofile
        assert pofile.getoutput() == expectedpo

    def test_preserve_format(self):
        """Tests that the layout of the po doesn't change unnecessarily"""
        templatepo = '''msgid "First part\\nSecond part"\nmsgstr ""\n"Eerste deel\\nTweede deel"\n\n'''
        mergepo = '''msgid "First part\\n"\n"Second part"\nmsgstr ""\n"Eerste deel\\n"\n"Tweede deel"'''
        pofile = self.mergepo(templatepo, mergepo)
        assert str(pofile) == templatepo

        templatepo = '''msgid "Use a scissor"\nmsgstr "Gebruik 'n sker "\n"om dit te doen"\n'''
        mergepo = '''msgid "Use a scissor"\nmsgstr "Gebruik 'n skêr om dit te doen"\n'''
        expectedpo = '''msgid "Use a scissor"\nmsgstr "Gebruik 'n skêr "\n"om dit te doen"\n\n'''
        pofile = self.mergepo(templatepo, mergepo)
        assert str(pofile) == expectedpo

        templatepo = '''msgid "To do it, use a scissor, please."\nmsgstr "Om dit te doen, "\n"gebruik 'n sker, "\n"asseblief."\n'''
        mergepo = '''msgid "To do it, use a scissor, please."\nmsgstr "Om dit te doen, gebruik 'n skêr, asseblief."\n'''
        expectedpo = '''msgid "To do it, use a scissor, please."\nmsgstr "Om dit te doen, "\n"gebruik 'n skêr, "\n"asseblief."\n\n'''
        pofile = self.mergepo(templatepo, mergepo)
        assert str(pofile) == expectedpo
        mergepo = '''msgid "To do it, use a scissor, please."\nmsgstr "Om dit te doen, gebruik 'n skêr, "\n"asseblief."\n'''
        pofile = self.mergepo(templatepo, mergepo)
        assert str(pofile) == expectedpo
        mergepo = '''msgid "To do it, use a scissor, please."\nmsgstr ""\n"Om dit te doen, "\n"gebruik 'n skêr, asseblief."\n'''
        pofile = self.mergepo(templatepo, mergepo)
        assert str(pofile) == expectedpo

        mergepo = '''msgid ""\n"To do it, use a scissor, "\n"please."\nmsgstr ""\n"Om dit te doen, "\n"gebruik 'n skêr, asseblief."\n'''
        pofile = self.mergepo(templatepo, mergepo)
        assert str(pofile) == expectedpo

        templatepo = '''msgid "To do it, use a scissor, please."\nmsgstr ""\n"Om dit te doen, "\n"gebruik 'n sker, "\n"asseblief."\n'''
        mergepo = '''msgid "To do it, use a scissor, please."\nmsgstr "Om dit te doen, gebruik 'n skêr, asseblief."\n'''
        expectedpo = '''msgid "To do it, use a scissor, please."\nmsgstr ""\n"Om dit te doen, "\n"gebruik 'n skêr, "\n"asseblief."\n\n'''
        pofile = self.mergepo(templatepo, mergepo)
        assert str(pofile) == expectedpo

        mergepo = '''msgid "To do it, use a scissor, please."\nmsgstr ""\n"Om dit te doen, gebruik 'n skêr, asseblief."\n'''
        pofile = self.mergepo(templatepo, mergepo)
        assert str(pofile) == expectedpo

    def test_preserve_format_kde_comments(self):
        """Test that layout related to KDE comments does not change unnecessarily"""
        templatepo = '''msgid "_: KDE comment\\n"\n"Simple string"\nmsgstr ""\n'''
        mergepo = '''msgid "_: KDE comment\\n"\n"Simple string"\nmsgstr "Dimpled ring"\n'''
        expectedpo = '''msgid "_: KDE comment\\n"\n"Simple string"\nmsgstr "Dimpled ring"\n\n'''
        pofile = self.mergepo(templatepo, mergepo)
        print "Expected:\n%s\n\nMerged:\n%s" % (expectedpo, str(pofile))
        assert str(pofile) == expectedpo

        templatepo = '''msgid ""\n"_: KDE comment\\n"\n"Simple string"\nmsgstr ""\n'''
        mergepo = '''msgid ""\n"_: KDE comment\\n"\n"Simple string"\nmsgstr "Dimpled ring"\n'''
        expectedpo = '''msgid ""\n"_: KDE comment\\n"\n"Simple string"\nmsgstr "Dimpled ring"\n\n'''
        pofile = self.mergepo(templatepo, mergepo)
        print "Expected:\n%s\n\nMerged:\n%s" % (expectedpo, str(pofile))
        assert str(pofile) == expectedpo

        templatepo = '''msgid ""\n"_: KDE "\n"comment\\n"\n"Simple string"\nmsgstr ""\n'''
        mergepo = '''msgid ""\n"_: KDE "\n"comment\\n"\n"Simple string"\nmsgstr "Dimpled ring"\n'''
        expectedpo = '''msgid ""\n"_: KDE "\n"comment\\n"\n"Simple string"\nmsgstr "Dimpled ring"\n\n'''
        pofile = self.mergepo(templatepo, mergepo)
        print "Expected:\n%s\n\nMerged:\n%s" % (expectedpo, str(pofile))
        assert str(pofile) == expectedpo

    def test_preserve_format_trailing_newlines(self):
        """Test that we can merge messages correctly that end with a newline"""
        templatepo = '''msgid "Simple string\\n"\nmsgstr ""\n'''
        mergepo = '''msgid "Simple string\\n"\nmsgstr "Dimpled ring\\n"\n'''
        expectedpo = '''msgid "Simple string\\n"\nmsgstr "Dimpled ring\\n"\n\n'''
        pofile = self.mergepo(templatepo, mergepo)
        print "Expected:\n%s\n\nMerged:\n%s" % (expectedpo, str(pofile))
        assert str(pofile) == expectedpo

        templatepo = '''msgid ""\n"Simple string\\n"\nmsgstr ""\n'''
        mergepo = '''msgid ""\n"Simple string\\n"\nmsgstr ""\n"Dimpled ring\\n"\n'''
        expectedpo = '''msgid ""\n"Simple string\\n"\nmsgstr "Dimpled ring\\n"\n\n'''
        pofile = self.mergepo(templatepo, mergepo)
        print "Expected:\n%s\n\nMerged:\n%s" % (expectedpo, str(pofile))
        assert str(pofile) == expectedpo

    def test_preserve_format_minor_start_and_end_of_sentence_changes(self):
        """Test that we are not too fussy about large diffs for simple changes at the start or end of a sentence"""
        templatepo = '''msgid "Target type:"\nmsgstr "Doelsoort"\n\n'''
        mergepo = '''msgid "Target type:"\nmsgstr "Doelsoort:"\n\n'''
        expectedpo = mergepo
        pofile = self.mergepo(templatepo, mergepo)
        print "Expected:\n%s\n\nMerged:\n%s" % (expectedpo, str(pofile))
        assert str(pofile) == expectedpo

        templatepo = '''msgid "&Select"\nmsgstr "Kies"\n\n'''
        mergepo = '''msgid "&Select"\nmsgstr "&Kies"\n\n'''
        expectedpo = mergepo
        pofile = self.mergepo(templatepo, mergepo)
        print "Expected:\n%s\n\nMerged:\n%s" % (expectedpo, str(pofile))
        assert str(pofile) == expectedpo

        templatepo = '''msgid "en-us, en"\nmsgstr "en-us, en"\n'''
        mergepo = '''msgid "en-us, en"\nmsgstr "af-za, af, en-za, en-gb, en-us, en"\n\n'''
        expectedpo = mergepo
        pofile = self.mergepo(templatepo, mergepo)
        print "Expected:\n%s\n\nMerged:\n%s" % (expectedpo, str(pofile))
        assert str(pofile) == expectedpo

    def test_preserve_format_last_entry_in_a_file(self):
        """The last entry in a PO file is usualy not followed by an empty line.  Test that we preserve this"""
        templatepo = '''msgid "First"\nmsgstr ""\n\nmsgid "Second"\nmsgstr ""\n'''
        mergepo = '''msgid "First"\nmsgstr "Eerste"\n\nmsgid "Second"\nmsgstr "Tweede"\n'''
        expectedpo = '''msgid "First"\nmsgstr "Eerste"\n\nmsgid "Second"\nmsgstr "Tweede"\n'''
        pofile = self.mergepo(templatepo, mergepo)
        print "Expected:\n%s\n\nMerged:\n%s" % (expectedpo, str(pofile))
        assert str(pofile) == expectedpo

        templatepo = '''msgid "First"\nmsgstr ""\n\nmsgid "Second"\nmsgstr ""\n\n'''
        mergepo = '''msgid "First"\nmsgstr "Eerste"\n\nmsgid "Second"\nmsgstr "Tweede"\n'''
        expectedpo = '''msgid "First"\nmsgstr "Eerste"\n\nmsgid "Second"\nmsgstr "Tweede"\n\n'''
        pofile = self.mergepo(templatepo, mergepo)
        print "Expected:\n%s\n\nMerged:\n%s" % (expectedpo, str(pofile))
        assert str(pofile) == expectedpo

    def test_preserve_format_tabs(self):
        templatepo = '''msgid "First	Second"\nmsgstr ""\n\n'''
        mergepo = '''msgid "First	Second"\nmsgstr "Eerste	Tweede"\n\n'''
        expectedpo = mergepo
        pofile = self.mergepo(templatepo, mergepo)
        print "Expected:\n%s\n\nMerged:\n%s" % (expectedpo, str(pofile))
        assert str(pofile) == expectedpo

    def test_preserve_comments_layout(self):
        """Ensure that when we merge with new '# (poconflict)' or other comments that we don't mess formating"""
        templatepo = '''#: filename\nmsgid "Desktop Background.bmp"\nmsgstr "Desktop Background.bmp"\n\n'''
        mergepo = '''# (pofilter) unchanged: please translate\n#: filename\nmsgid "Desktop Background.bmp"\nmsgstr "Desktop Background.bmp"\n\n'''
        expectedpo = mergepo
        pofile = self.mergepo(templatepo, mergepo)
        print "Expected:\n%s\n\nMerged:\n%s" % (expectedpo, str(pofile))
        assert str(pofile) == expectedpo

    def test_merge_dos2unix(self):
        """Test that merging a comment line with dos newlines doesn't add a new line"""
        templatepo = '''# User comment\n# (pofilter) Translate Toolkit comment\n#. Automatic comment\n#: location_comment.c:110\nmsgid "File"\nmsgstr "File"\n\n'''
        mergepo =  '''# User comment\r\n# (pofilter) Translate Toolkit comment\r\n#. Automatic comment\r\n#: location_comment.c:110\r\nmsgid "File"\r\nmsgstr "Ifayile"\r\n\r\n'''
        expectedpo = '''# User comment\n# (pofilter) Translate Toolkit comment\n#. Automatic comment\n#: location_comment.c:110\nmsgid "File"\nmsgstr "Ifayile"\n\n'''
        pofile = self.mergepo(templatepo, mergepo)
        assert str(pofile) == expectedpo

        # Unassociated comment
        templatepo = '''# Lonely comment\n\n#: location_comment.c:110\nmsgid "Bob"\nmsgstr "Toolmaker"\n'''
        mergepo = '''# Lonely comment\r\n\r\n#: location_comment.c:110\r\nmsgid "Bob"\r\nmsgstr "Builder"\r\n\r\n'''
        expectedpo = '''# Lonely comment\n\n#: location_comment.c:110\nmsgid "Bob"\nmsgstr "Builder"\n\n'''
        pofile = self.mergepo(templatepo, mergepo)
        assert str(pofile) == expectedpo

        # New comment
        templatepo = '''#: location_comment.c:110\nmsgid "File"\nmsgstr "File"\n\n'''
        mergepo =  '''# User comment\r\n# (pofilter) Translate Toolkit comment\r\n#: location_comment.c:110\r\nmsgid "File"\r\nmsgstr "Ifayile"\r\n\r\n'''
        expectedpo = '''# User comment\n# (pofilter) Translate Toolkit comment\n#: location_comment.c:110\nmsgid "File"\nmsgstr "Ifayile"\n\n'''
        pofile = self.mergepo(templatepo, mergepo)
        assert str(pofile) == expectedpo

    def xtest_xliff_into_xliff(self):
        templatexliff = self.xliffskeleton % '''<trans-unit>
        <source>red</source>
        <target></target>
</trans-unit>'''
        mergexliff = self.xliffskeleton % '''<trans-unit>
        <source>red</source>
        <target>rooi</target>
</trans-unit>'''
        xlifffile = self.mergexliff(templatexliff, mergexliff)
        assert len(xlifffile.units) == 1
        unit = xlifffile.units[0]
        assert unit.source == "red"
        assert unit.target== "rooi"

    def xtest_po_into_xliff(self):
        templatexliff = self.xliffskeleton % '''<trans-unit>
        <source>red</source>
        <target></target>
</trans-unit>'''
        mergepo = 'msgid "red"\nmsgstr "rooi"'
        xlifffile = self.mergexliff(templatexliff, mergepo)
        assert len(xlifffile.units) == 1
        unit = xlifffile.units[0]
        assert unit.source == "red"
        assert unit.target== "rooi"
        
    def xtest_xliff_into_po(self):
        templatepo = '# my comment\nmsgid "red"\nmsgstr ""'
        mergexliff = self.xliffskeleton % '''<trans-unit>
        <source>red</source>
        <target>rooi</target>
</trans-unit>'''
        expectedpo = '# my comment\nmsgid "red"\nmsgstr "rooi"\n\n'
        pofile = self.mergepo(templatepo, mergexliff)
        assert str(pofile) == expectedpo

    def test_merging_dont_merge_kde_comments_found_in_translation(self):
        """If we find a KDE comment in the translation and it is exactly the same as the English then do not merge it"""
        templatepo = '''msgid "_: KDE comment\\n"\n"File"\nmsgstr "File"\n\n'''
        mergepo = '''msgid "_: KDE comment\\n"\n"File"\nmsgstr "_: KDE comment\\n"\n"Ifayile"\n\n'''
        expectedpo = '''msgid "_: KDE comment\\n"\n"File"\nmsgstr "Ifayile"\n\n'''
        pofile = self.mergepo(templatepo, mergepo)
        print "Expected:\n%s\n\nMerged:\n%s" % (expectedpo, str(pofile))
        assert str(pofile) == expectedpo
        
        # multiline KDE comment
        templatepo = '''msgid "_: KDE "\n"comment\\n"\n"File"\nmsgstr "File"\n\n'''
        mergepo = '''msgid "_: KDE "\n"comment\\n"\n"File"\nmsgstr "_: KDE "\n"comment\\n"\n"Ifayile"\n\n'''
        expectedpo = '''msgid "_: KDE "\n"comment\\n"\n"File"\nmsgstr "Ifayile"\n\n'''
        pofile = self.mergepo(templatepo, mergepo)
        print "Expected:\n%s\n\nMerged:\n%s" % (expectedpo, str(pofile))
        assert str(pofile) == expectedpo

    def test_merging_untranslated_with_kde_disambiguation(self):
        """test merging untranslated messages that are the same except for KDE disambiguation"""
        templatepo = r'''#: sendMsgTitle
#: sendMsgTitle.accesskey
msgid "_: sendMsgTitle sendMsgTitle.accesskey\n"
"Send Message"
msgstr ""

#: sendMessageCheckWindowTitle
#: sendMessageCheckWindowTitle.accesskey
msgid "_: sendMessageCheckWindowTitle sendMessageCheckWindowTitle.accesskey\n"
"Send Message"
msgstr ""
'''
        mergepo = r'''#: sendMsgTitle
#: sendMsgTitle.accesskey
msgid "_: sendMsgTitle sendMsgTitle.accesskey\n"
"Send Message"
msgstr "Stuur"

#: sendMessageCheckWindowTitle
#: sendMessageCheckWindowTitle.accesskey
msgid "_: sendMessageCheckWindowTitle sendMessageCheckWindowTitle.accesskey\n"
"Send Message"
msgstr "Stuur"

'''
        expectedpo = mergepo
        pofile = self.mergepo(templatepo, mergepo)
        print "Expected:\n%s\n---\nMerged:\n%s\n---" % (expectedpo, str(pofile))
        assert str(pofile) == expectedpo

