#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2007 Zuza Software Foundation
# 
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""Module to provide a cache of statistics in a database.

@organization: Zuza Software Foundation
@copyright: 2007 Zuza Software Foundation
@license: U{GPL <http://www.fsf.org/licensing/licenses/gpl.html>}
"""

from translate import __version__ as toolkitversion
from translate.storage import factory, base
from translate.misc.multistring import multistring
from translate.lang.common import Common

import os.path
import re
import sys
import stat

kdepluralre = re.compile("^_n: ")
brtagre = re.compile("<br\s*?/?>")
xmltagre = re.compile("<[^>]+>")
numberre = re.compile("\\D\\.\\D")

state_strings = {0: "untranslated", 1: "translated", 2: "fuzzy"}

def wordcount(string):
    # TODO: po class should understand KDE style plurals
    string = kdepluralre.sub("", string)
    string = brtagre.sub("\n", string)
    string = xmltagre.sub("", string)
    string = numberre.sub(" ", string)
    #TODO: This should still use the correct language to count in the target 
    #language
    return len(Common.words(string))

def wordsinunit(unit):
    """Counts the words in the unit's source and target, taking plurals into 
    account. The target words are only counted if the unit is translated."""
    (sourcewords, targetwords) = (0, 0)
    if isinstance(unit.source, multistring):
        sourcestrings = unit.source.strings
    else:
        sourcestrings = [unit.source or ""]
    for s in sourcestrings:
        sourcewords += wordcount(s)
    if not unit.istranslated():
        return sourcewords, targetwords
    if isinstance(unit.target, multistring):
        targetstrings = unit.target.strings
    else:
        targetstrings = [unit.target or ""]
    for s in targetstrings:
        targetwords += wordcount(s)
    return sourcewords, targetwords

def statefordb(unit):
    """Returns the numeric database state for the unit."""
    if unit.istranslated():
        return 1
    if unit.isfuzzy() and unit.target:
        return 2
    return 0

def emptystats():
    """Returns a dictionary with all statistics initalised to 0."""
    stats = {}
    for state in ["total", "translated", "fuzzy", "untranslated", "review"]:
        stats[state] = 0
        stats[state + "sourcewords"] = 0
        stats[state + "targetwords"] = 0
    return stats

# We allow the caller to specify which value to return when errors_return_empty
# is True. We do this, since Poolte wants None to be returned when it calls
# get_mod_info directly, whereas we want an integer to be returned for 
# uses of get_mod_info within this module.
# TODO: Get rid of empty_return when Pootle code is improved to not require
#       this.
def get_mod_info(file_path, errors_return_empty=False, empty_return=0):
    try:
        file_stat = os.stat(file_path)
        assert not stat.S_ISDIR(file_stat.st_mode)
        return (file_stat.st_mtime, file_stat.st_size)
    except:
        if errors_return_empty:
            return empty_return
        else:
            raise

def suggestioninfo(filename, **kwargs):
    """Provides the filename of the associated file containing suggestions and 
    its mod_info, if it exists."""
    root, ext = os.path.splitext(filename)
    suggestion_filename = None
    suggestion_mod_info = -1
    if ext == os.path.extsep + "po":
        # For a PO file there might be an associated file with suggested
        # translations. If either file changed, we want to regenerate the
        # statistics.
        suggestion_filename = filename + os.path.extsep + 'pending'
        if not os.path.exists(suggestion_filename):
            suggestion_filename = None
        else:
            suggestion_mod_info = get_mod_info(suggestion_filename, **kwargs)
    return suggestion_filename, suggestion_mod_info

def parse_mod_info(string):
    try:
        tokens = string.strip("()").split(",")
        if os.stat_float_times():
            return (float(tokens[0]), long(tokens[1]))
        else:
            return (int(tokens[0]), long(tokens[1]))
    except:
        return (-1, -1)

def dump_mod_info(mod_info):
    return str(mod_info)
