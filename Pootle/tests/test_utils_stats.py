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

class TestStats:
    def test_classification(self):
        posource = '''msgid "Simple String"\nmsgstr "Dimpled ring"\n'''
        openedfile = StringIO.StringIO(posource)
        po_obj = po.pofile(openedfile)

        d = stats.enumerating_classify(checks.StandardChecker(), po_obj.units)
        
        expected_result = { 
            'acronyms': [], 
            'escapes': [], 
            'tabs': [], 
            'unchanged': [], 
            'blank': [], 
            'validchars': [], 
            'numbers': [], 
            'printf': [], 
            'accelerators': [], 
            'total': [0], 
            'doublewords': [], 
            'newlines': [], 
            'puncspacing': [], 
            'functions': [], 
            'simplecaps': [], 
            'spellcheck': [], 
            'doublequoting': [], 
            'brackets': [], 
            'untranslated': [], 
            'endwhitespace': [], 
            'long': [], 
            'targetwordcount': [2], 
            'notranslatewords': [], 
            'compendiumconflicts': [], 
            'filepaths': [], 
            'startwhitespace': [], 
            'variables': [], 
            'doublespacing': [], 
            'startpunc': [], 
            'startcaps': [], 
            'fuzzy': [], 
            'purepunc': [], 
            'kdecomments': [], 
            'singlequoting': [], 
            'emails': [], 
            'musttranslatewords': [], 
            'short': [], 
            'endpunc': [], 
            'xmltags': [], 
            'has-suggestions': [], 
            'urls': [], 
            'translated': [0], 
            'sentencecount': [], 
            'simpleplurals': [], 
            'sourcewordcount': [2]
            }
        for key in d.iterkeys():
            assert d[key] == expected_result[key]
        
       
    def test_classification_two(self):
        data = stats.enumerating_classify(checks.StandardChecker(), test_po.units)

        expected_result = {
            'check-untranslated': [100, 107, 154, 155, 156, 160, 161, 162, 216, 217, 218, 219, 220, 221, 222, 223, 224, 226, 227, 228, 229, 232, 248, 264, 272], 
            'check-unchanged': [244, 259, 260], 
            'acronyms': [], 
            'check-doublespacing': [62], 
            'escapes': [], 
            'tabs': [], 
            'check-startpunc': [80, 145, 243, 273], 
            'unchanged': [], 
            'blank': [100, 107, 154, 155, 156, 160, 161, 162, 216, 217, 218, 219, 220, 221, 222, 223, 224, 226, 227, 228, 229, 232, 248, 264, 272, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306], 
            'validchars': [], 
            'numbers': [], 
            'printf': [], 
            'accelerators': [], 
            'check-endpunc': [0, 79, 163, 225, 230, 231, 233, 236, 273], 
            'check-xmltags': [0, 66, 145, 273], 
            'total': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306], 
            'doublewords': [], 
            'newlines': [], 
            'puncspacing': [], 
            'functions': [], 
            'simplecaps': [], 
            'spellcheck': [], 
            'doublequoting': [], 
            'brackets': [], 
            'check-simplecaps': [0, 6, 14, 96, 136, 137, 139, 140, 152, 159, 190, 225, 243], 
            'untranslated': [], 
            'endwhitespace': [], 
            'long': [], 
            'targetwordcount': [37, 3, 1, 1, 1, 1, 2, 1, 2, 2, 1, 1, 2, 2, 4, 2, 2, 3, 2, 2, 3, 3, 3, 3, 2, 2, 1, 3, 3, 3, 3, 3, 3, 2, 2, 4, 4, 3, 1, 3, 1, 3, 2, 5, 2, 2, 4, 8, 3, 2, 4, 4, 16, 13, 11, 3, 3, 5, 1, 1, 2, 3, 41, 20, 24, 1, 13, 5, 5, 2, 3, 2, 13, 6, 6, 2, 1, 3, 3, 6, 6, 1, 5, 1, 9, 10, 2, 2, 3, 1, 6, 2, 2, 4, 6, 2, 2, 2, 3, 2, 2, 1, 0, 3, 2, 2, 5, 2, 2, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 4, 3, 3, 4, 5, 6, 2, 2, 2, 3, 5, 2, 4, 4, 2, 4, 4, 4, 2, 4, 3, 3, 2, 3, 2, 2, 1, 1, 3, 2, 3, 2, 2, 2, 2, 1, 1, 3, 1, 0, 0, 0, 2, 2, 1, 0, 0, 0, 4, 9, 10, 6, 9, 1, 1, 1, 1, 1, 3, 1, 1, 8, 9, 8, 9, 8, 8, 8, 9, 8, 9, 5, 3, 1, 1, 2, 8, 3, 5, 6, 3, 3, 2, 7, 4, 3, 7, 2, 3, 2, 1, 6, 7, 2, 2, 2, 6, 6, 8, 8, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 3, 3, 0, 6, 9, 11, 7, 3, 7, 7, 13, 13, 7, 6, 1, 1, 1, 1, 0, 4, 7, 1, 2, 6, 2, 1, 2, 9, 10, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 3, 0, 2, 4, 2, 3, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
            'notranslatewords': [], 
            'check-emails': [0], 
            'compendiumconflicts': [], 
            'check-doublequoting': [64], 
            'filepaths': [], 
            'startwhitespace': [], 
            'variables': [], 
            'check-endwhitespace': [0, 225, 230, 231], 
            'check-filepaths': [66], 
            'doublespacing': [], 
            'startpunc': [], 
            'startcaps': [], 
            'fuzzy': [66, 74, 79, 80, 108, 144, 145, 151, 152, 153, 157, 158, 159, 181, 225, 230, 231, 236, 243], 
            'purepunc': [], 
            'kdecomments': [], 
            'singlequoting': [], 
            'emails': [], 
            'musttranslatewords': [], 
            'short': [], 
            'endpunc': [], 
            'xmltags': [], 
            'check-sentencecount': [0, 163, 233, 236], 
            'check-brackets': [0, 64, 66], 
            'check-newlines': [0, 225, 230, 231], 
            'has-suggestions': [], 
            'urls': [], 
            'check-startcaps': [0, 80, 145, 159, 243, 273], 
            'translated': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 67, 68, 69, 70, 71, 72, 73, 75, 76, 77, 78, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 101, 102, 103, 104, 105, 106, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 146, 147, 148, 149, 150, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 233, 234, 235, 237, 238, 239, 240, 241, 242, 244, 245, 246, 247, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 265, 266, 267, 268, 269, 270, 271, 273, 274, 275, 276, 277, 278], 
            'sentencecount': [], 
            'simpleplurals': [], 
            'sourcewordcount': [0, 2, 1, 1, 1, 1, 2, 1, 2, 2, 1, 1, 2, 2, 3, 2, 2, 3, 2, 2, 3, 3, 2, 2, 2, 2, 1, 2, 3, 2, 2, 2, 3, 2, 1, 4, 2, 3, 1, 3, 1, 3, 2, 4, 2, 2, 3, 10, 3, 2, 4, 3, 11, 11, 10, 2, 1, 4, 1, 1, 2, 2, 48, 22, 17, 1, 13, 4, 4, 2, 2, 2, 11, 5, 5, 2, 1, 2, 2, 5, 5, 1, 5, 1, 6, 10, 2, 2, 3, 1, 3, 2, 2, 4, 4, 2, 2, 2, 3, 2, 2, 1, 1, 2, 1, 1, 3, 2, 2, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 5, 4, 6, 2, 2, 2, 2, 3, 2, 3, 3, 2, 4, 4, 4, 2, 4, 2, 2, 2, 3, 2, 2, 1, 1, 2, 3, 2, 2, 2, 2, 2, 1, 1, 2, 2, 1, 2, 2, 2, 2, 1, 2, 1, 2, 4, 8, 8, 4, 9, 1, 1, 1, 1, 1, 3, 1, 1, 8, 9, 9, 10, 9, 9, 9, 9, 9, 9, 3, 1, 1, 1, 1, 5, 2, 3, 6, 3, 3, 2, 5, 3, 2, 5, 2, 3, 2, 1, 3, 3, 2, 2, 2, 4, 4, 6, 6, 8, 12, 12, 10, 12, 14, 3, 11, 12, 7, 5, 17, 29, 21, 10, 5, 4, 6, 5, 5, 9, 6, 2, 5, 5, 11, 11, 6, 6, 1, 1, 1, 1, 1, 3, 7, 1, 2, 6, 2, 1, 2, 8, 9, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 17, 2, 4, 2, 3, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
            'check-printf': [66, 80, 225, 230, 231, 243], 
            'check-doublewords': [50, 74]
            }

        for key in data.iterkeys():
            assert data[key] == expected_result[key]

class TestFilter:
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

