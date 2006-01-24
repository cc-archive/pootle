#!/usr/bin/env python

"""tests for storage base classes"""

from translate.storage import base
from py import test
import os

class TestTranslationUnit:
    """Tests a TranslationUnit.
    Derived classes can reuse these tests by pointing UnitClass to a derived Unit"""
    UnitClass = base.TranslationUnit
    def test_create(self):
        """tests a simple creation with a source string"""
        unit = self.UnitClass("Test String")
        assert unit.source == "Test String"

    def test_eq(self):
        """tests equality comparison"""
        unit1 = self.UnitClass("Test String")
        unit2 = self.UnitClass("Test String")
        unit3 = self.UnitClass("Blessed String")
        assert unit1 == unit1
        assert unit1 == unit2
        assert unit1 != unit3

class TestTranslationStore:
    """Tests a TranslationStore.
    Derived classes can reuse these tests by pointing StoreClass to a derived Store"""
    StoreClass = base.TranslationStore

    def setup_method(self, method):
        """Allocates a unique self.filename for the method, making sure it doesn't exist"""
        self.filename = "%s_%s.test" % (self.__class__.__name__, method.__name__)
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def teardown_method(self, method):
        """Makes sure that if self.filename was created by the method, it is cleaned up"""
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_create_blank(self):
        """Tests creating a new blank store"""
        store = self.StoreClass()
        assert len(store.units) == 0

    def test_add(self):
        """Tests adding a new unit with a source string"""
        store = self.StoreClass()
        unit = store.addsourceunit("Test String")
        assert len(store.units) == 1
        assert unit.source == "Test String"

    def test_find(self):
        """Tests searching for a given source string"""
        store = self.StoreClass()
        unit1 = store.addsourceunit("Test String")
        unit2 = store.addsourceunit("Blessed String")
        assert store.findunit("Test String") == unit1
        assert store.findunit("Blessed String") == unit2
        assert test.raises(KeyError, store.findunit, ("Nest String",))

    def test_parse(self):
        """Tests converting to a string and parsing the resulting string"""
        store = self.StoreClass()
        unit1 = store.addsourceunit("Test String")
        unit2 = store.addsourceunit("Blessed String")
        saved_store = str(store)
        newstore = self.StoreClass.parsestring(saved_store)
        assert len(newstore.units) == len(store.units)
        for n, unit in enumerate(store.units):
            assert newstore.units[n] == unit

    def test_files(self):
        """Tests saving to and loading from files"""
        store = self.StoreClass()
        unit1 = store.addsourceunit("Test String")
        unit2 = store.addsourceunit("Blessed String")
        store.savefile(self.filename)
        newstore = self.StoreClass.parsefile(self.filename)
        assert len(newstore.units) == len(store.units)
        for n, unit in enumerate(store.units):
            assert newstore.units[n] == unit

