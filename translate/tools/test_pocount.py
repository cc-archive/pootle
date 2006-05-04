#!/usr/bin/env python

from translate.tools import pocount
from translate.storage import po
from translate.misc import wStringIO

class TestPOCount:
    def count(self, source, expectedsource, target=None, expectedtarget=None):
        """simple helper to check the respective word counts"""
        poelement = po.pounit(source)
        if target is not None:
          poelement.settarget(target)
        wordssource, wordstarget = pocount.wordsinpoel(poelement)
        print 'Source (expected=%d; actual=%d): "%s"' % (expectedsource, wordssource, source)
        assert wordssource == expectedsource
        if target is not None:
          print 'Target (expected=%d; actual=%d): "%s"' % (expectedtarget, wordstarget, target)
          assert wordstarget == expectedtarget

    def test_simple_count_zero(self):
        """no content"""
        self.count("", 0)

    def test_simple_count_one(self):
        """simplest one word count"""
        self.count("One", 1)

    def test_simple_count_two(self):
        """simplest one word count"""
        self.count("One two", 2)

    def test_punctuation_only(self):
        """test a message with only punctuation"""
        self.count(",", 1)

    def test_punctuation_divides_words(self):
        """test that we break words when there is punctuation"""
        self.count("One. Two", 2)
        #FIXME: 
	self.count("One.Two", 2)

    def test_xml_tags(self):
        """test that we do not count XML tags as words"""
        # FIXME (we're not treating <br> as a word break) 
	self.count("A word<br>Another word", 4)
        # FIXME (we're not trating \n as a word break) 
	self.count("<p>A word</p>\n<p>Another word</p>", 4)

    def test_newlines(self):
        """test to see that newlines divide words"""
        #FIXME (newlines should break words) 
	self.count("A word.\nAnother word", 4)
        #FIXME (newlines should break words) 
	self.count(r"A word.\\n\nAnother word", 4)

    def test_variables_are_words(self):
        """test that we count variables as words"""
        self.count("%PROGRAMNAME %PROGRAM% %s $file $1", 5)

    def test_kde_comments_are_not_counted(self):
        """test that we do not add KDE comments to the wordcount"""
        #FIXME (we don't seem to be eliminating KDE comment) 
	self.count("_: This is a seven word comment\\n\nOne two three", 3, "Een twee drie", 3)

    def test_plurals(self):
        """test that we can handle plural PO elements"""
        # #: gdk-pixbuf/gdk-pixdata.c:430
        # #, c-format
        # msgid "failed to allocate image buffer of %u byte"
        # msgid_plural "failed to allocate image buffer of %u bytes"
        # msgstr[0] "e paletšwe go hwetša sešireletši sa seswantšho sa paete ya %u"
        # msgstr[1] "e paletšwe go hwetša sešireletši sa seswantšho sa dipaete tša %u"

    def test_plurals_kde(self):
        """test that we correcly count old style KDE plurals"""
	self.count("_n: Singular\\n\nPlural", 2, "Een\\n\ntwee\\n\ndrie", 3)

    def test_msgid_blank(self):
        """counts a message id"""
        self.count("   ", 0)

    # Counting strings
    #  We need to check how we count strings also and if we call it translated or untranslated
    # ie an all spaces msgid should be translated if there are spaces in the msgstr
   
    # Make sure we don't count obsolete messages

    # Do we correctly identify a translated yet blank message?

    # Need to test that we can differentiate between fuzzy, translated and untranslated

