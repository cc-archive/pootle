#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2002, 2003 Zuza Software Foundation
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

"""this is a set of string filters that should be run before the results are analysed..."""

from translate.misc import quote
import sre
from translate.filters import helpers
from translate.filters import decoration

# filters that the string is passed through before certain tests:

def removekdecomments(str1):
  """removed kde-style po comments i.e. starting with _: and ending with litteral \\n"""
  iskdecomment = False
  lines = str1.split("\n")
  removelines = []
  for linenum in range(len(lines)):
    line = lines[linenum]
    if line.startswith("_:"):
      lines[linenum] = ""
      iskdecomment = True
    if iskdecomment:
      removelines.append(linenum)
    if line.strip() and not iskdecomment:
      break
    if iskdecomment and line.strip().endswith("\\n"):
      iskdecomment = False
  lines = [lines[linenum] for linenum in range(len(lines)) if linenum not in removelines]
  return "\n".join(lines)

ignoreaccelerators = []

def filteraccelerators(accelmarker):
  """returns a function that filters accelerators marked using accelmarker in strings"""
  if accelmarker is None: accelmarkerlen = 0
  else: accelmarkerlen = len(accelmarker)
  def filtermarkedaccelerators(str1):
    """modifies the accelerators in str1 marked with a given marker, using a given filter"""
    acclocs = decoration.findaccelerators(str1, accelmarker, ignoreaccelerators)
    fstr1, pos = "", 0
    for accelstart, accelerator in acclocs:
      fstr1 += str1[pos:accelstart]
      fstr1 += accelerator
      pos = accelstart + accelmarkerlen + len(accelerator)
    fstr1 += str1[pos:]
    return fstr1
  return filtermarkedaccelerators

ignorevariables = ["amp"]

def varname(variable, startmarker, endmarker):
  """a simple variable filter that returns the variable name without the marking punctuation"""
  return variable
  # if the punctuation were included, we'd do the following:
  if startmarker is None:
    return variable[:variable.rfind(endmarker)]
  elif endmarker is None:
    return variable[variable.find(startmarker)+len(startmarker):]
  else:
    return variable[variable.find(startmarker)+len(startmarker):variable.rfind(endmarker)]

def filtervariables(startmarker, endmarker, varfilter):
  """returns a function that filters variables marked using startmarker and endmarker in strings"""
  if startmarker is None: startmarkerlen = 0
  else: startmarkerlen = len(startmarker)
  if endmarker is None: endmarkerlen = 0
  elif type(endmarker) == int: endmarkerlen = 0
  else: endmarkerlen = len(endmarker)
  def filtermarkedvariables(str1):
    """modifies the variables in str1 marked with a given marker, using a given filter"""
    varlocs = decoration.findmarkedvariables(str1, startmarker, endmarker)
    fstr1, pos = "", 0
    for varstart, variable in varlocs:
      fstr1 += str1[pos:varstart]
      fstr1 += varfilter(variable, startmarker, endmarker)
      pos = varstart + startmarkerlen + len(variable) + endmarkerlen
    fstr1 += str1[pos:]
    return fstr1
  return filtermarkedvariables

# a list of special words with punctuation 
# all apostrophes in the middle of the word are handled already
wordswithpunctuation = ["'n","'t" # Afrikaans
                       ]
# map all the words to their non-punctified equivalent
wordswithpunctuation = dict([(word, filter(str.isalnum, word)) for word in wordswithpunctuation])

def filterwordswithpunctuation(str1):
  """goes through a list of known words that have punctuation and removes the punctuation from them"""
  occurrences = []
  for word, replacement in wordswithpunctuation.iteritems():
    occurrences.extend([(pos, word, replacement) for pos in quote.find_all(str1, word)])
  for match in sre.finditer("\w+'\w+", str1):
    word = match.group()
    if isinstance(word, unicode):
      replacement = filter(unicode.isalnum, word)
    else:
      replacement = filter(str.isalnum, word)
    occurrences.append((match.start(), word, replacement))
  occurrences.sort()
  replacements = []
  for pos, word, replacement in occurrences:
    previouschar = (pos == 0) and " " or str1[pos-1]
    nextchar = (pos+len(word) == len(str1)) and " " or str1[pos+len(word)]
    if (previouschar.isspace() or previouschar == '"') and (nextchar.isspace() or nextchar == '"'):
      replacements.append((pos, word, replacement))
  if replacements:
    lastpos = 0
    newstr1 = ""
    for pos, word, replacement in replacements:
      newstr1 += str1[lastpos:pos]
      newstr1 += replacement
      lastpos = pos + len(word)
    newstr1 += str1[lastpos:]
    return newstr1
  else:
    return str1


