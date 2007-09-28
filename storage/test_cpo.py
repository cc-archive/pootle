#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.storage import cpo as po
from translate.storage import test_po
from translate.misc.multistring import multistring
from translate.misc import wStringIO
from py.test import raises

class TestCPOUnit(test_po.TestPOUnit):
    UnitClass = po.pounit

    def test_plurals(self):
        """Tests that plurals are handled correctly."""
        unit = self.UnitClass("Cow")
        unit.msgid_plural = ["Cows"]
        assert isinstance(unit.source, multistring)
        assert unit.source.strings == ["Cow", "Cows"]
        assert unit.source == "Cow"

        unit.target = ["Koei", "Koeie"]
        assert isinstance(unit.target, multistring)
        assert unit.target.strings == ["Koei", "Koeie"]
        assert unit.target == "Koei"

        unit.target = {0:"Koei", 3:"Koeie"}
        assert isinstance(unit.target, multistring)
        assert unit.target.strings == ["Koei", "Koeie"]
        assert unit.target == "Koei"

        unit.target = [u"Sk\u00ear", u"Sk\u00eare"]
        assert isinstance(unit.target, multistring)
        assert unit.target.strings == [u"Sk\u00ear", u"Sk\u00eare"]
        assert unit.target.strings == [u"Sk\u00ear", u"Sk\u00eare"]
        assert unit.target == u"Sk\u00ear"

    def test_plural_reduction(self):
        """checks that reducing the number of plurals supplied works"""
        unit = self.UnitClass("Tree")
        unit.msgid_plural = ["Trees"]
        assert isinstance(unit.source, multistring)
        assert unit.source.strings == ["Tree", "Trees"]
        unit.target = multistring(["Boom", "Bome", "Baie Bome"])
        assert isinstance(unit.source, multistring)
        assert unit.target.strings == ["Boom", "Bome", "Baie Bome"]
        unit.target = multistring(["Boom", "Bome"])
        assert unit.target.strings == ["Boom", "Bome"]
        unit.target = "Boom"
        # FIXME: currently assigning the target to the same as the first string won't change anything
        # we need to verify that this is the desired behaviour...
        assert unit.target.strings == ["Boom", "Bome"]
        unit.target = "Een Boom"
        assert unit.target.strings == ["Een Boom"]

    def test_notes(self):
        """tests that the generic notes API works"""
        unit = self.UnitClass("File")
        assert unit.getnotes() == ""
        unit.addnote("Which meaning of file?")
        assert unit.getnotes("translator") == "Which meaning of file?"
        assert unit.getnotes("developer") == ""
        unit.addnote("Verb", origin="programmer")
        assert unit.getnotes("developer") == "Verb"
        unit.addnote("Thank you", origin="translator")
        assert unit.getnotes("translator") == "Which meaning of file?\nThank you"
        assert unit.getnotes() == "Which meaning of file?\nThank you\nVerb"
        assert raises(ValueError, unit.getnotes, "devteam")

    def test_notes_withcomments(self):
        """tests that when we add notes that look like comments that we treat them properly"""
        unit = self.UnitClass("File")
        unit.addnote("# Double commented comment")
        assert unit.getnotes() == "# Double commented comment"

class TestCPOFile(test_po.TestPOFile):
    StoreClass = po.pofile
    def test_msgidcomments(self):
        """checks that we handle msgid comments"""
        posource = 'msgid "test me"\nmsgstr ""'
        pofile = self.poparse(posource)
        thepo = pofile.units[0]
        thepo.msgidcomment = "first comment"
        print pofile
        print "Blah", thepo.source
        assert thepo.source == "test me"
        thepo.msgidcomment = "second comment"
        assert str(pofile).count("_:") == 1

#    def test_merge_duplicates(self):
#        """checks that merging duplicates works"""
#        posource = '#: source1\nmsgid "test me"\nmsgstr ""\n\n#: source2\nmsgid "test me"\nmsgstr ""\n'
#        pofile = self.poparse(posource)
#        assert len(pofile.units) == 2
#        pofile.removeduplicates("merge")
#        assert len(pofile.units) == 1
#        assert pofile.units[0].getlocations() == ["source1", "source2"]

#    def test_merge_duplicates_msgctxt(self):
#        """checks that merging duplicates works for msgctxt"""
#        posource = '#: source1\nmsgid "test me"\nmsgstr ""\n\n#: source2\nmsgid "test me"\nmsgstr ""\n'
#        pofile = self.poparse(posource)
#        assert len(pofile.units) == 2
#        pofile.removeduplicates("msgctxt")
#        print pofile
#        assert len(pofile.units) == 2
#        assert str(pofile.units[0]).count("source1") == 2
#        assert str(pofile.units[1]).count("source2") == 2
  
    def test_parse_context(self):
        """Tests that msgctxt is parsed correctly and that it is accessible via the api methods."""
        posource = '''# Test comment
#: source1
msgctxt "noun"
msgid "convert"
msgstr "bekeerling"

# Test comment 2
#: source2
msgctxt "verb"
msgid "convert"
msgstr "omskakel"
'''
        pofile = self.poparse(posource)
        unit = pofile.units[0]

        assert unit.getcontext() == 'noun'
        assert unit.getnotes() == ' Test comment'

        unit = pofile.units[1]
        assert unit.getcontext() == 'verb'
        assert unit.getnotes() == ' Test comment 2'


    def test_parse_advanced_context(self):
        """Tests that some weird possible msgctxt scenarios are parsed correctly."""
        posource = r'''# Test multiline context
#: source1
msgctxt "Noun."
" A person that changes his or her ways."
msgid "convert"
msgstr "bekeerling"

# Test quotes
#: source2
msgctxt "Verb. Converting from \"something\" to \"something else\"."
msgid "convert"
msgstr "omskakel"

# Test quotes, newlines and multiline.
#: source3
msgctxt "Verb.\nConverting from \"something\""
" to \"something else\"."
msgid "convert"
msgstr "omskakel"
'''
        pofile = self.poparse(posource)
        unit = pofile.units[0]

        assert unit.getcontext() == 'Noun. A person that changes his or her ways.'
        assert unit.getnotes() == ' Test multiline context'

        unit = pofile.units[1]
        assert unit.getcontext() == 'Verb. Converting from "something" to "something else".'
        assert unit.getnotes() == ' Test quotes'
        
        unit = pofile.units[2]
        assert unit.getcontext() == 'Verb.\nConverting from "something" to "something else".'
        assert unit.getnotes() == ' Test quotes, newlines and multiline.'
 
    def test_kde_context(self):
        """Tests that kde-style msgid comments can be retrieved via getcontext()."""
        posource = '''# Test comment
#: source1
msgid ""
"_: Noun\\n"
"convert"
msgstr "bekeerling"

# Test comment 2
#: source2
msgid ""
"_: Verb. _: "
"The action of changing.\\n"
"convert"
msgstr "omskakel"
'''
        pofile = self.poparse(posource)
        unit = pofile.units[0]

        assert unit.getcontext() == 'Noun'
        assert unit.getnotes() == ' Test comment'

        unit = pofile.units[1]
        assert unit.getcontext() == 'Verb. _: The action of changing.'
        assert unit.getnotes() == ' Test comment 2'

#    def test_merge_mixed_sources(self):
#        """checks that merging works with different source location styles"""
#        posource = '''
##: source1
##: source2
#msgid "test"
#msgstr ""
#
##: source1 source2
#msgid "test"
#msgstr ""
#'''
#        pofile = self.poparse(posource)
#        print str(pofile)
#        assert len(pofile.units) == 2
#        pofile.removeduplicates("merge")
#        print str(pofile)
#        assert len(pofile.units) == 1
#        assert pofile.units[0].getlocations() == ["source1", "source2"]

#    def test_merge_blanks(self):
#        """checks that merging adds msgid_comments to blanks"""
#        posource = '#: source1\nmsgid ""\nmsgstr ""\n\n#: source2\nmsgid ""\nmsgstr ""\n'
#        pofile = self.poparse(posource)
#        assert len(pofile.units) == 2
#        pofile.removeduplicates("merge")
#        assert len(pofile.units) == 2
#        print pofile.units[0].msgidcomments
#        print pofile.units[1].msgidcomments
#        assert po.unquotefrompo(pofile.units[0].msgidcomments) == "_: source1\n"
#        assert po.unquotefrompo(pofile.units[1].msgidcomments) == "_: source2\n"

#    def test_msgid_comment(self):
#        """checks that when adding msgid_comments we place them on a newline"""
#        posource = '#: source0\nmsgid "Same"\nmsgstr ""\n\n#: source1\nmsgid "Same"\nmsgstr ""\n'
#        pofile = self.poparse(posource)
#        assert len(pofile.units) == 2
#        pofile.removeduplicates("msgid_comment")
#        assert len(pofile.units) == 2
#        assert po.unquotefrompo(pofile.units[0].msgidcomments) == "_: source0\n"
#        assert po.unquotefrompo(pofile.units[1].msgidcomments) == "_: source1\n"
#        # Now lets check for formating
#        for i in (0, 1):
#          expected = '''#: source%d\nmsgid ""\n"_: source%d\\n"\n"Same"\nmsgstr ""\n''' % (i, i)
#          assert pofile.units[i].__str__() == expected

#    def test_keep_blanks(self):
#        """checks that keeping keeps blanks and doesn't add msgid_comments"""
#        posource = '#: source1\nmsgid ""\nmsgstr ""\n\n#: source2\nmsgid ""\nmsgstr ""\n'
#        pofile = self.poparse(posource)
#        assert len(pofile.units) == 2
#        pofile.removeduplicates("keep")
#        assert len(pofile.units) == 2
#        # check we don't add msgidcomments
#        assert po.unquotefrompo(pofile.units[0].msgidcomments) == ""
#        assert po.unquotefrompo(pofile.units[1].msgidcomments) == ""

    def test_output_str_unicode(self):
        """checks that we can str(pofile) which is in unicode"""
        posource = u'''#: nb\nmsgid "Norwegian Bokm\xe5l"\nmsgstr ""\n'''
        pofile = self.StoreClass(wStringIO.StringIO(posource.encode("UTF-8")), encoding="UTF-8")
        assert len(pofile.units) == 1
        print str(pofile)
        thepo = pofile.units[0]
#        assert str(pofile) == posource.encode("UTF-8")
        # extra test: what if we set the msgid to a unicode? this happens in prop2po etc
        thepo.source = u"Norwegian Bokm\xe5l"
#        assert str(thepo) == posource.encode("UTF-8")
        # Now if we set the msgstr to Unicode
        # this is an escaped half character (1/2)
        halfstr = "\xbd ...".decode("latin-1")
        thepo.target = halfstr
#        assert halfstr in str(pofile).decode("UTF-8")
        thepo.target = halfstr.encode("UTF-8")
#        assert halfstr.encode("UTF-8") in str(pofile)

    def test_posections(self):
        """checks the content of all the expected sections of a PO message"""
        posource = '# other comment\n#. automatic comment\n#: source comment\n#, fuzzy\nmsgid "One"\nmsgstr "Een"\n'
        pofile = self.poparse(posource)
        print pofile
        assert len(pofile.units) == 1
        assert str(pofile) == posource

    def test_obsolete(self):
        """Tests that obsolete messages work"""
        posource = '#~ msgid "Old thing"\n#~ msgstr "Ou ding"\n'
        pofile = self.poparse(posource)
        #assert pofile.isempty()
        assert len(pofile.units) == 1
        assert pofile.units[0].isobsolete()
        assert str(pofile) == posource

    def test_makeobsolete(self):
        """Tests making a unit obsolete"""
        posource = '#. The automatic one\n#: test.c\nmsgid "test"\nmsgstr "rest"\n'
        poexpected = '#. The automatic one\n#: test.c\n#~ msgid "test"\n#~ msgstr "rest"\n'
        pofile = self.poparse(posource)
        print pofile
        unit = pofile.units[0]
        assert not unit.isobsolete()
        unit.makeobsolete()
        assert unit.isobsolete()
        print pofile
        assert str(pofile) == poexpected
        
    def test_makeobsolete_plural(self):
        """Tests making a plural unit obsolete"""
        posource = r'''msgid "Cow"
msgid_plural "Cows"
msgstr[0] "Koei"
msgstr[1] "Koeie"
'''
        poexpected = '''#~ msgid "Cow"
#~ msgid_plural "Cows"
#~ msgstr[0] "Koei"
#~ msgstr[1] "Koeie"
'''
        pofile = self.poparse(posource)
        print pofile
        unit = pofile.units[0]
        assert not unit.isobsolete()
        unit.makeobsolete()
        assert unit.isobsolete()
        print pofile
        assert str(pofile) == poexpected

    def test_makeobsolete_msgctxt(self):
        """Tests making a unit with msgctxt obsolete"""
        posource = '#: test.c\nmsgctxt "Context"\nmsgid "test"\nmsgstr "rest"\n'
        poexpected = '#: test.c\n#~ msgctxt "Context"\n#~ msgid "test"\n#~ msgstr "rest"\n'
        pofile = self.poparse(posource)
        print pofile
        unit = pofile.units[0]
        assert not unit.isobsolete()
        unit.makeobsolete()
        assert unit.isobsolete()
        print pofile
        assert str(pofile) == poexpected

    def test_makeobsolete_msgidcomments(self):
        """Tests making a unit with msgidcomments obsolete"""
        posource = '#: first.c\nmsgid ""\n"_: first.c\\n"\n"test"\nmsgstr "rest"\n\n#: second.c\nmsgid ""\n"_: second.c\\n"\n"test"\nmsgstr "rest"'
        poexpected = '#: second.c\nmsgid ""\n"_: second.c\\n"\n"test"\nmsgstr "rest"\n\n#: first.c\n#~ msgid ""\n#~ "_: first.c\\n"\n#~ "test"\n#~ msgstr "rest"\n'
        print "Source:\n%s" % posource
        print "Expected:\n%s" % poexpected
        pofile = self.poparse(posource)
        unit = pofile.units[0]
        assert not unit.isobsolete()
        unit.makeobsolete()
        assert unit.isobsolete()
        print "Result:\n%s" % pofile
        assert str(pofile) == poexpected

    def test_multiline_obsolete(self):
        """Tests for correct output of mulitline obsolete messages"""
        posource = '#~ msgid ""\n#~ "Old thing\\n"\n#~ "Second old thing"\n#~ msgstr ""\n#~ "Ou ding\\n"\n#~ "Tweede ou ding"\n'
        pofile = self.poparse(posource)
        print "Source:\n%s" % posource
        print "Output:\n%s" % str(pofile)
        assert len(pofile.units) == 1
        assert pofile.units[0].isobsolete()
        assert not pofile.units[0].istranslatable()
        assert str(pofile) == posource

    def test_unassociated_comments(self):
        """tests behaviour of unassociated comments."""
        oldsource = '# old lonesome comment\n\nmsgid "one"\nmsgstr "een"\n'
        oldfile = self.poparse(oldsource)
        print "__str__", str(oldfile)
        assert len(oldfile.units) == 1
        assert str(oldfile).find("# old lonesome comment\nmsgid") >= 0
    
