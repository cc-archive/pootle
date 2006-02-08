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

    def test_simpleentry_quickhelptest(self):
        """checks that a simple entry with quickhelptext is parsed correctly"""
        oosource = r'sd	source\ui\dlg\sdobjpal.src	0	imagebutton	FLTWIN_SDOBJPALETTE	BTN_SYMSIZE			16	en-US	-		Toggle Symbol Size		20051017 21:40:56'
        oofile = self.ooparse(oosource)
        assert len(oofile.ooelements) == 1
        oe = oofile.ooelements[0]
        assert oe.languages.keys() == ["en-US"]
        ol = oofile.oolines[0]
        assert ol.getkey() == ('sd', r'source\ui\dlg\sdobjpal.src', 'imagebutton', 'FLTWIN_SDOBJPALETTE', 'BTN_SYMSIZE', '')
        assert ol.quickhelptext == 'Toggle Symbol Size'
        assert str(ol) == oosource

    def test_simpleentry_title(self):
        """checks that a simple entry with title text is parsed correctly"""
        oosource = r'dbaccess	source\ui\dlg\indexdialog.src	0	querybox	QUERY_SAVE_CURRENT_INDEX				0	en-US	Do you want to save the changes made to the current index?			Exit Index Design	20051017 21:40:56'
        oofile = self.ooparse(oosource)
        assert len(oofile.ooelements) == 1
        oe = oofile.ooelements[0]
        assert oe.languages.keys() == ["en-US"]
        ol = oofile.oolines[0]
        assert ol.getkey() == ('dbaccess', r'source\ui\dlg\indexdialog.src', 'querybox', 'QUERY_SAVE_CURRENT_INDEX', '', '')
        assert ol.title == 'Exit Index Design'
        assert str(ol) == oosource

    def test_blankline(self):
        """checks that a blank line is parsed correctly"""
        oosource = '\n'
        warnings.simplefilter("error")
        oofile = self.ooparse(oosource)
        assert len(oofile.ooelements) == 0

