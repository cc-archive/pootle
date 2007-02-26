#!/usr/bin/env python
# -*- coding: utf-8 -*-

from translate.lang import factory

def test_getlanguage():
    """Tests that a basic call to getlanguage() works."""
    kmlanguage = factory.getlanguage('km')
    assert kmlanguage.code == 'km'
    assert kmlanguage.fullname == 'Khmer'
    
    # Test a non-exisint code
    language = factory.getlanguage('zz')
    assert language.nplurals == 0

    # Test a code without a module
    language = factory.getlanguage('fy')
    assert language.nplurals == 2
    assert language.fullname == "Frisian"

    # Test a code without a module and with a country code
    language = factory.getlanguage('de_AT')
    assert language.nplurals == 2
    assert language.fullname == "German"

    # Test with None as language code
    language = factory.getlanguage(None)
    assert language.code == ''
