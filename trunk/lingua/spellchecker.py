#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2005 Dwayne Bailey
#
# This file is part of the translate toolkit
#
# The translate toolkit is free software; you can redistribute it and/or modify
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

"""A class provides wrappers for various spell checkers currently on Microsoft Word spell
checker but this will be expanded to include ispell, aspell, myspell and any other spell
you would love to have."""

import sys
if sys.platform == "win32":
  import win32com.client

class BaseSpell:

  def suggest(self, word):
    return "some words that we suggest"

  def check(self, word):
    return True

class MSSpell:

  customdict = ""
  ignoreuppercase = False

  def __init__(language):

    msword = win32com.client.Dispatch('Word.Application')
    msword.Visible = False
    worddoc = msword.Documents.Add()
    self.language = language

  def __destroy__():
    worddoc.Close()

  def suggest(self, word):
    return self.msword.GetSpellingSuggestions(Word=word, CustomDictionary=self.customdict, IgnoreUppercase=self.ignoreuppercase, MainDictionary=self.language)

  def check(self, word):
    return not self.msword.CheckSpelling(Word=word, CustomDictionary=self.customdict, IgnoreUppercase=self.ignoreuppercase)

