#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2002-2006 Zuza Software Foundation
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


"""script that converts a .po file with translations based on a .pot file
generated from a Mozilla localization .properties back to the .properties (but translated)
Uses the original .properties to do the conversion as this makes sure we don't
leave out any unexpected stuff..."""

from translate.misc import quote
from translate.storage import po
from translate.storage import properties
from translate import __version__

eol = "\n"

class reprop:
  def __init__(self, templatefile):
    self.templatefile = templatefile
    self.podict = {}

  def convertfile(self, pofile, includefuzzy=False):
    self.inmultilinemsgid = 0
    self.inecho = 0
    self.makepodict(pofile, includefuzzy)
    outputlines = []
    for line in self.templatefile.readlines():
      outputstr = self.convertline(line)
      outputlines.append(outputstr)
    return outputlines

  def makepodict(self, pofile, includefuzzy=False):
    # make a dictionary of the translations
    for thepo in pofile.units:
      if includefuzzy or not thepo.isfuzzy():
        # there may be more than one entity due to msguniq merge
        for entity in thepo.getlocations():
          propstring = thepo.target
	  
          # NOTE: triple-space as a string means leave it empty (special signal)
          if len(propstring.strip()) == 0 and propstring != "   ":
	    propstring = thepo.source
          self.podict[entity] = propstring

  def convertline(self, line):
    returnline = ""
    # handle multiline msgid if we're in one
    if self.inmultilinemsgid:
      msgid = quote.rstripeol(line).strip()
      # see if there's more
      self.inmultilinemsgid = (msgid[-1:] == '\\')
      # if we're echoing...
      if self.inecho:
        returnline = line
    # otherwise, this could be a comment
    elif line.strip()[:1] == '#':
      returnline = quote.rstripeol(line)+eol
    else:
      equalspos = line.find('=')
      # if no equals, just repeat it
      if equalspos == -1:
        returnline = quote.rstripeol(line)+eol
      # otherwise, this is a definition
      else:
        # backslash at end means carry string on to next line
        if quote.rstripeol(line)[-1:] == '\\':
          self.inmultilinemsgid = 1
        # now deal with the current string...
        name = line[:equalspos].strip()
        if self.podict.has_key(name):
          self.inecho = 0
          postr = self.podict[name]
          if isinstance(postr, str):
            postr = postr.decode('utf8')
          returnline = name+"="+quote.mozillapropertiesencode(postr)+eol
        else:
          self.inecho = 1
          returnline = line+eol
    if isinstance(returnline, unicode):
      returnline = returnline.encode('utf-8')
    return returnline

def convertprop(inputfile, outputfile, templatefile, includefuzzy=False):
  inputpo = po.pofile(inputfile)
  if templatefile is None:
    raise ValueError("must have template file for properties files")
    # convertor = po2prop()
  else:
    convertor = reprop(templatefile)
  outputproplines = convertor.convertfile(inputpo, includefuzzy)
  outputfile.writelines(outputproplines)
  return 1

def main(argv=None):
  # handle command line options
  from translate.convert import convert
  formats = {("po", "properties"): ("properties", convertprop)}
  parser = convert.ConvertOptionParser(formats, usetemplates=True, description=__doc__)
  parser.add_fuzzy_option()
  parser.run(argv)

if __name__ == '__main__':
  main()

