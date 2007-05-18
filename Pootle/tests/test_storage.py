#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""tests for stats classes"""

from py import test
from Pootle.storage.storagelayout import gettext_path
from Pootle.storage_client import get_unit, post_unit

from Pootle.path import path
import os
import zipfile

# set up test PO
testdir = os.sep.join(__file__.split(os.sep)[:-1])
test_path = path(os.path.join(testdir, "testroot"))
test_po = test_path.translationstore


testroots = ['storage_testroot1.zip']

def setup(zipped_root):
    if test_path.exists():
        test_path.rmtree()
    test_path.mkdir()
    zipped = zipfile.ZipFile(zipped_root, 'r')
    for name in zipped.namelist():
        f = (test_path / name)
        if f.endswith('/'):
            f.mkdir()
        else:
            f.write_bytes(zipped.read(name))

def cleanup():
    test_path.rmtree()

class TestStorage:
    def test_index(self):
        for root in testroots:
            setup(root)
            t = gettext_path(test_path / 'test' / 'test.po')
            # test.po exists
            assert(t.exists() == True)
            
            # index rebuild
            t.index.remove()
            t.update_index()
            assert(t.index.exists() == True)

            data = '0000000025                     \n0000000001 00000000000000000000\n0000000673 00000000000000000000\n0000000736 00000000000000000000\n0000000812 00000000000000000000\n0000000867 00000000000000000000\n0000000967 00000000000000000000\n0000001033 00000000000000000000\n0000001102 00000000000000000000\n0000001176 00000000000000000000\n0000001227 00000000000000000000\n0000001308 00000000000000000000\n0000001451 00000000000000000000\n0000001647 00000000000000000000\n0000001780 00000000000000000000\n0000001896 00000000000000000000\n0000002026 00000000000000000000\n0000002152 00000000000000000000\n0000002272 00000000000000000000\n0000002390 00000000000000000000\n0000002546 00000000000000000000\n0000002674 00000000000000000000\n0000002797 00000000000000000000\n0000002943 00000000000000000000\n0000003101 00000000000000000000\n0000003450 00000000000000000000\n'
            assert(t.index.bytes() == data)

            # automatic index rebuild
            t.index.remove()
            t[2]
            assert(t.index.exists() == True)
            assert(t.index.bytes() == data)
            
    def test_storage_client__get_unit(self):
        for root in testroots:
            print 'test'
            setup(root)
            
            unit, info = get_unit('test/test.po',3)
            assert str(unit) == 'msgid "Suggest"\nmsgstr "Predlagaj"\n\n'

    def test_storage_client__post_unit(self):
        setup(testroots[0])

        unit1, info = get_unit('test/test.po',3)
        unit1.settarget("To je novi target")
        unit, info = post_unit('test/test.po',3, unit1)

        assert str(unit) == 'msgid "Suggest"\nmsgstr "To je novi target"\n'

