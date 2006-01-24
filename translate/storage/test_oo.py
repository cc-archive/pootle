#!/usr/bin/env python

from translate.storage import oo
from translate.misc import wStringIO
import warnings

class TestOO:
    def setup_method(self, method):
        warnings.resetwarnings()

    def teardown_method(self, method):
        warnings.resetwarnings()

    def ooparse(self, oosource):
        """helper that parses oo source without requiring files"""
        dummyfile = wStringIO.StringIO(oosource)
        oofile = oo.oofile(dummyfile)
        return oofile

    def ooregen(self, oosource):
        """helper that converts oo source to oofile object and back"""
        return str(self.ooparse(oosource))

    def test_simpleentry(self):
        """checks that a simple oo entry is parsed correctly"""
        oosource = r'svx	source\dialog\numpages.src	0	string	RID_SVXPAGE_NUM_OPTIONS	STR_BULLET			0	en-US	Character				20050924 09:13:58'
        oofile = self.ooparse(oosource)
        assert len(oofile.ooelements) == 1
        oe = oofile.ooelements[0]
        assert oe.languages.keys() == ["en-US"]
        ol = oofile.oolines[0]
        assert ol.getkey() == ('svx', r'source\dialog\numpages.src', 'string', 'RID_SVXPAGE_NUM_OPTIONS', 'STR_BULLET', '')
        assert ol.text == 'Character'
        assert str(ol) == oosource

    def test_blankline(self):
        """checks that a blank line is parsed correctly"""
        oosource = '\n'
        warnings.simplefilter("error")
        oofile = self.ooparse(oosource)
        assert len(oofile.ooelements) == 0

