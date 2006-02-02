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
        """helper that converts prop source to propfile object and back"""
        return str(self.propparse(propsource))

    def test_simpleentry(self):
        """checks that a simple properties entry is parsed correctly"""
        propsource = 'test=testvalue'
        propfile = self.propparse(propsource)
        assert len(propfile.propelements) == 1
        theprop = propfile.propelements[0]
        assert theprop.name == "test"
        assert theprop.msgid == "testvalue"

    def test_simpleregen(self):
        """checks that a simple properties entry is regenerated correctly"""
        propsource = 'test=testvalue'
        regensource = self.propregen(propsource).rstrip("\n")
        assert regensource == propsource

