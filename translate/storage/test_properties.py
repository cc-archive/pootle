#!/usr/bin/env python

from translate.storage import properties
from translate.misc import wStringIO

class TestProperties:
    def propparse(self, propsource):
        """helper that parses properties source without requiring files"""
        dummyfile = wStringIO.StringIO(propsource)
        propfile = properties.propfile(dummyfile)
        return propfile

    def propregen(self, propsource):
        """helper that converts properties source to propfile object and back"""
        return str(self.propparse(propsource))

    def test_simpledefinition(self):
        """checks that a simple properties definition is parsed correctly"""
        propsource = 'test_me=I can code!'
        propfile = self.propparse(propsource)
        assert len(propfile.propelements) == 1
        propelement = propfile.propelements[0]
        assert propelement.name == "test_me"
        assert propelement.msgid == "I can code!"

    def test_simpledefinition_source(self):
        """checks that a simple properties definition can be regenerated as source"""
        propsource = 'test_me=I can code!\n'
        propregen = self.propregen(propsource)
        assert propsource == propregen

