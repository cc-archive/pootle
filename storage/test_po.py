#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.storage import po
from translate.storage import test_base

class TestPOUnit(test_base.TestTranslationUnit):
    UnitClass = po.pounit

class TestPOFile(test_base.TestTranslationStore):
    StoreClass = po.pofile
