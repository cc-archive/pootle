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

"""classes that hold elements of comma-separated values (.csv) files (csvelement)
or entire files (csvfile) for use with localisation
"""

try:
  # try to import the standard csv module, included from Python 2.3
  import csv
except:
  # if it doesn't work, use our local copy of it...
  from translate.misc import csv

from translate.misc import sparse

class SimpleDictReader:
  def __init__(self, fileobj, fieldnames):
    self.fieldnames = fieldnames
    self.contents = fileobj.read()
    self.parser = sparse.SimpleParser(defaulttokenlist=[",", "\n"],whitespacechars="\r")
    self.parser.stringescaping = 0
    self.parser.quotechars = '"'
    self.tokens = self.parser.tokenize(self.contents)
    self.tokenpos = 0

  def __iter__(self):
    return self

  def getvalue(self, value):
    """returns a value, evaluating strings as neccessary"""
    if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
      return sparse.stringeval(value).replace("\r","").replace("\n","")
    else:
      return value

  def next(self):
    while self.tokenpos < len(self.tokens) and self.tokens[self.tokenpos] == "\n":
      self.tokenpos += 1
    if self.tokenpos >= len(self.tokens):
      raise StopIteration()
    thistokens = []
    while self.tokenpos < len(self.tokens) and self.tokens[self.tokenpos] != "\n":
      thistokens.append(self.tokens[self.tokenpos])
      self.tokenpos += 1
    while self.tokenpos < len(self.tokens) and self.tokens[self.tokenpos] == "\n":
      self.tokenpos += 1
    fields = []
    # patch together fields since we can have quotes inside a field
    currentfield = ''
    fieldparts = 0
    for token in thistokens:
      if token == ',':
        # a field is only quoted if the whole thing is quoted
        if fieldparts == 1:
          currentfield = self.getvalue(currentfield)
        fields.append(currentfield)
        currentfield = ''
        fieldparts = 0
      else:
        currentfield += token
        fieldparts += 1
    # things after the last comma...
    if fieldparts:
      if fieldparts == 1:
        currentfield = self.getvalue(currentfield)
      fields.append(currentfield)
    values = {}
    for fieldnum in range(len(self.fieldnames)):
      if fieldnum >= len(fields):
        values[self.fieldnames[fieldnum]] = ""
      else:
        values[self.fieldnames[fieldnum]] = fields[fieldnum]
    return values

class csvelement:
  def __init__(self):
    self.source = ""
    self.msgid = ""
    self.msgstr = ""

  def fromdict(self, cedict):
    self.source = cedict.get('source', '')
    self.msgid = cedict.get('msgid', '')
    self.msgstr = cedict.get('msgstr', '')
    if self.source is None: self.source = ''
    if self.msgid is None: self.msgid = ''
    if self.msgstr is None: self.msgstr = ''
    if self.msgid[:2] in ("\\+", "\\-"): self.msgid = self.msgid[1:]
    if self.msgstr[:2] in ("\\+", "\\-"): self.msgstr = self.msgstr[1:]

  def todict(self):
    return {'source':self.source, 'msgid':self.msgid, 'msgstr':self.msgstr}

class csvfile:
  def __init__(self, inputfile=None):
    self.csvelements = []
    self.fieldnames = ['source', 'msgid', 'msgstr']
    self.filename = getattr(inputfile, 'name', '')
    if inputfile is not None:
      csvlines = inputfile.readlines()
      inputfile.close()
      self.fromlines(csvlines)

  def fromlines(self,lines):
    if type(lines) == list: lines = "".join(lines)
    csvfile = csv.StringIO(lines)
    reader = SimpleDictReader(csvfile, self.fieldnames)
    for row in reader:
      newce = csvelement()
      newce.fromdict(row)
      self.csvelements.append(newce)

  def tolines(self):
    csvfile = csv.StringIO()
    writer = csv.DictWriter(csvfile, self.fieldnames)
    for ce in self.csvelements:
      cedict = ce.todict()
      writer.writerow(cedict)
    csvfile.reset()
    return csvfile.readlines()

if __name__ == '__main__':
  import sys
  cf = csvfile()
  cf.fromlines(sys.stdin.readlines())
  sys.stdout.writelines(cf.tolines())

