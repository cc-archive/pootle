#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""tests for stats classes"""

from py import test
from Pootle.utils import stats
from Pootle.path import path
from translate.filters import checks
from translate.storage import po
import os
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO


# set up test PO
testdir = os.sep.join(__file__.split(os.sep)[:-1])
test_path = path(os.path.join(testdir, "sample.po"))
test_po = test_path.translationstore

class TestPath:
    def test_filter(self):
        next, unit = test_path.filter(['translated'],1)
        assert next == 65
        next, unit = test_path.filter(['translated'],next)
        assert next == 73

    def test_iterfilter(self):
        result = []
        for c in test_path.iterfilter(['translated']): 
            result.append(c[0])
        assert result == [65, 73, 78, 79, 99, 106, 107, 143, 144, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 180, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 235, 242, 247, 263, 271]

    def test_stats(self):
        assert test_path.stats == [824,234,84,113,19,6,157,25,8,1102,278]
        # cleanup fstags entry
        del test_path._stats

    
