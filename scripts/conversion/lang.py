#!/usr/bin/env python

# lang.py
# Defines standard translation-toolkit structions for .lang files 

# Author: Dan Schafer <dschafer@mozilla.com>
# Date: 10 Jun 2008

from translate.storage import base
from translate.storage import txt 

class LangUnit(base.TranslationUnit):
  """This is just a normal unit with a weird string output"""
  def __str__(self):
    return ";%s\n%s" % (str(self.source), str(self.target))

class LangStore(txt.TxtFile):
  """We extend TxtFile, since that has a lot of useful stuff for encoding"""
  UnitClass = LangUnit

  def parse(self, lines):
    if not isinstance(lines, list):
      lines = lines.split("\n")
    for linenum in range(len(lines)):
      line = lines[linenum].rstrip("\n").rstrip("\r")
      if len(line) == 0:
        continue
      if line[0] == ';':
        u = self.addsourceunit(line[1:])
        u.addlocation("%s:%d" % (self.filename, linenum+1))
      else:
        u.settarget(line)

  def __str__(self):
    return "\n\n".join([str(unit) for unit in self.units])
