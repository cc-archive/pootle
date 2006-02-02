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

    def singleentry(self, propfile):
        """checks that a propfile has a single entry, and returns it"""
        assert len(propfile.propelements) == 1
        theprop = propfile.propelements[0]
        return theprop

    def test_simpleentry(self):
        """checks that a simple properties entry is parsed correctly"""
        propsource = 'test=testvalue'
        propfile = self.propparse(propsource)
        theprop = self.singleentry(propfile)
        assert theprop.name == "test"
        assert theprop.msgid == "testvalue"

    def test_simpleregen(self):
        """checks that a simple properties entry is regenerated correctly"""
        propsource = 'test=testvalue'
        regensource = self.propregen(propsource).rstrip("\n")
        assert regensource == propsource

    def test_multiline(self):
        """checks that multiline enties can be parsed"""
        propsource = r"""5093=Unable to connect to your IMAP server. You may have exceeded the maximum number \
of connections to this server. If so, use the Advanced IMAP Server Settings dialog to \
reduce the number of cached connections."""
        propfile = self.propparse(propsource)
        theprop = self.singleentry(propfile)
        assert theprop.name == "5093"
        assert theprop.msgid.startswith("Unable")
        assert theprop.msgid.endswith("cached connections.")
        assert "Advanced IMAP" in theprop.msgid

    def test_escapedcolon_end(self):
        """tests that escaped colons at end of string are handled"""
        propsource = r"EnterLinkText=Introduzca el texto a mostrar para el enlace\:"
        propfile = self.propparse(propsource)
        theprop = self.singleentry(propfile)
        assert theprop.name == "EnterLinkText"
        assert theprop.msgid == r'Introduzca el texto a mostrar para el enlace\:'

