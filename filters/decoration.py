#!/usr/bin/env python
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

"""functions to get decorative/informative text out of strings..."""

def spacestart(str1):
  """returns all the whitespace from the start of the string"""
  newstring = ""
  for c in str1:
    if not c.isspace(): return newstring
    else: newstring += c
  return newstring

def spaceend(str1):
  """returns all the whitespace from the end of the string"""
  newstring = ""
  for n in range(len(str1)):
    c = str1[-1-n]
    if not c.isspace(): return newstring
    else: newstring = c + newstring
  return newstring

def puncstart(str1):
  """returns all the punctuation from the start of the string"""
  newstring = ""
  for c in str1:
    if c.isalnum() or c >= '\x80': return newstring
    else: newstring += c
  return newstring

def puncend(str1):
  """returns all the punctuation from the end of the string"""
  newstring = ""
  for n in range(len(str1)):
    c = str1[-1-n]
    if c.isalnum() or c >= '\x80': return newstring
    else: newstring = c + newstring
  return newstring

def ispurepunctuation(str1):
  """checks whether the string is entirely punctuation"""
  for c in str1:
    if c.isalpha(): return 0
  return 1

def isvalidaccelerator(accelerator, ignorelist=[]):
  """returns whether the given accelerator string is a valid one..."""
  if len(accelerator) == 0 or accelerator in ignorelist:
    return 0
  accelerator = accelerator.replace("_","")
  return accelerator.isalnum()

def findaccelerators(str1, accelmarker, ignorelist=[]):
  """returns all the accelerators and locations in str1 marked with a given marker"""
  accelerators = []
  currentpos = 0
  while currentpos >= 0:
    currentpos = str1.find(accelmarker, currentpos)
    if currentpos >= 0:
      accelstart = currentpos
      currentpos += len(accelmarker)
      # we assume accelerators are single characters
      accelend = currentpos + 1
      if accelend > len(str1): break
      accelerator = str1[currentpos:accelend]
      currentpos = accelend
      if isvalidaccelerator(accelerator, ignorelist):
        accelerators.append((accelstart, accelerator))
  return accelerators

def findmarkedvariables(str1, startmarker, endmarker, ignorelist=[]):
  """returns all the variables and locations in str1 marked with a given marker"""
  variables = []
  currentpos = 0
  while currentpos >= 0:
    currentpos = str1.find(startmarker, currentpos)
    if currentpos >= 0:
      startmatch = currentpos
      currentpos += len(startmarker)
      if endmarker is None:
        # handle case without an end marker - use any non-alphanumeric character
        endmatch = currentpos
        for n in range(currentpos, len(str1)):
          if not str1[n].isalnum():
            endmatch = n
            break
        if currentpos == endmatch: endmatch = len(str1)
        variable = str1[currentpos:endmatch]
        currentpos = endmatch
      elif type(endmarker) == int:
        # setting endmarker to an int means it is a fixed-length variable string (usually endmarker==1)
        endmatch = currentpos + endmarker
        if endmatch > len(str1): break
        variable = str1[currentpos:endmatch]
        currentpos = endmatch
      else:
        endmatch = str1.find(endmarker, currentpos)
        if endmatch == -1: break
        # search backwards in case there's an intervening startmarker (if not it's OK)...
        start2 = str1.rfind(startmarker, currentpos, endmatch)
        if start2 != -1:
          startmatch2 = start2
          start2 += len(startmarker)
          if start2 != currentpos:
            currentpos = start2
            startmatch = startmatch2
        variable = str1[currentpos:endmatch]
        currentpos = endmatch + len(endmarker)
      if len(variable) > 0 and variable.replace("_","").isalnum() and (variable not in ignorelist):
        variables.append((startmatch, variable))
  return variables

def getaccelerators(accelmarker, ignorelist=[]):
  """returns a function that gets a list of accelerators marked using accelmarker"""
  def getmarkedaccelerators(str1):
    """returns all the accelerators in str1 marked with a given marker"""
    acclocs = findaccelerators(str1, accelmarker, ignorelist)
    accelerators = [accelerator for accelstart, accelerator in acclocs]
    return accelerators
  return getmarkedaccelerators

def getvariables(startmarker, endmarker):
  """returns a function that gets a list of variables marked using startmarker and endmarker"""
  def getmarkedvariables(str1):
    """returns all the variables in str1 marked with a given marker"""
    varlocs = findmarkedvariables(str1, startmarker, endmarker)
    variables = [variable for accelstart, variable in varlocs]
    return variables
  return getmarkedvariables

def getnumbers(str1):
  """returns any numbers that are in the string"""
  # TODO: handle locale-based periods e.g. 2,5 for Afrikaans
  numbers = []
  innumber = False
  lastnumber = ""
  carryperiod = ""
  for chr1 in str1:
    if chr1.isdigit():
      innumber = True
    elif innumber and chr1 == '.':
      pass
    elif innumber:
      innumber = False
      if lastnumber:
        numbers.append(lastnumber)
      lastnumber = ""
    if innumber:
      if chr1 == '.':
        carryperiod += chr1
      else:
        lastnumber += carryperiod + chr1
    else:
      carryperiod = ""
  if innumber:
    if lastnumber:
      numbers.append(lastnumber)
  return numbers

def countaccelerators(accelmarker, ignorelist=[]):
  """returns a function that counts the number of accelerators marked with the given marker"""
  def countmarkedaccelerators(str1):
    """returns all the variables in str1 marked with a given marker"""
    acclocs = findaccelerators(str1, accelmarker, ignorelist)
    return len(acclocs)
  return countmarkedaccelerators


