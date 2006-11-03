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

"""simple script to convert a mozilla .properties localization file to a
gettext .pot format for translation.
does a line-by-line conversion..."""

import sys
from translate.misc import quote
from translate.storage import po
from translate.storage import properties
from translate import __version__

eol = "\n"

class prop2po:
  """convert a .properties file to a .po file for handling the translation..."""
  def convertfile(self, thepropfile, duplicatestyle="msgid_comment"):
    """converts a .properties file to a .po file..."""
    thepofile = po.pofile()
    headerpo = thepofile.makeheader(charset="UTF-8", encoding="8bit", x_accelerator_marker="&")
    headerpo.othercomments.append("# extracted from %s\n" % thepropfile.filename)
    # we try and merge the header po with any comments at the start of the properties file
    appendedheader = 0
    waitingcomments = []
    for theprop in thepropfile.units:
      thepo = self.convertelement(theprop)
      if thepo is None:
        waitingcomments.extend(theprop.comments)
      if not appendedheader:
        if theprop.isblank():
          thepo = headerpo
        else:
          thepofile.units.append(headerpo)
        appendedheader = 1
      if thepo is not None:
        thepo.othercomments = waitingcomments + thepo.othercomments
        waitingcomments = []
        thepofile.units.append(thepo)
    thepofile.removeduplicates(duplicatestyle)
    return thepofile

  def mergefiles(self, origpropfile, translatedpropfile, blankmsgstr=False, duplicatestyle="msgid_comment"):
    """converts two .properties files to a .po file..."""
    thepofile = po.pofile()
    headerpo = thepofile.makeheader(charset="UTF-8", encoding="8bit")
    headerpo.othercomments.append("# extracted from %s, %s\n" % (origpropfile.filename, translatedpropfile.filename))
    translatedpropfile.makeindex()
    # we try and merge the header po with any comments at the start of the properties file
    appendedheader = 0
    waitingcomments = []
    # loop through the original file, looking at units one by one
    for origprop in origpropfile.units:
      origpo = self.convertelement(origprop)
      if origpo is None:
        waitingcomments.extend(origprop.comments)
      # handle the header case specially...
      if not appendedheader:
        if origprop.isblank():
          origpo = headerpo
        else:
          thepofile.units.append(headerpo)
        appendedheader = 1
      # try and find a translation of the same name...
      if origprop.name in translatedpropfile.locationindex:
        translatedprop = translatedpropfile.locationindex[origprop.name]
        translatedpo = self.convertelement(translatedprop)
      else:
        translatedpo = None
      # if we have a valid po element, get the translation and add it...
      if origpo is not None:
        if translatedpo is not None and not blankmsgstr:
          origpo.target = translatedpo.source
        origpo.othercomments = waitingcomments + origpo.othercomments
        waitingcomments = []
        thepofile.units.append(origpo)
      elif translatedpo is not None:
        print >>sys.stderr, "error converting original properties definition %s" % origprop.name
    thepofile.removeduplicates(duplicatestyle)
    return thepofile

  def convertelement(self, theprop):
    """Converts a .properties element to a .po element. Returns None if empty
    or not for translation."""
    if theprop is None:
      return None
    # escape unicode
    thepo = po.pounit(encoding="UTF-8")
    if hasattr(theprop, "comments"):
      for comment in theprop.comments:
        if "DONT_TRANSLATE" in comment:
          return None
      thepo.othercomments.extend(theprop.comments)
    # TODO: handle multiline msgid
    if theprop.isblank():
      return None
    thepo.sourcecomments.append("#: "+theprop.name+eol)
    thepo.source = theprop.source
    thepo.target = ""
    return thepo

def convertprop(inputfile, outputfile, templatefile, pot=False, duplicatestyle="msgctxt"):
  """reads in inputfile using properties, converts using prop2po, writes to outputfile"""
  inputprop = properties.propfile(inputfile)
  convertor = prop2po()
  if templatefile is None:
    outputpo = convertor.convertfile(inputprop, duplicatestyle=duplicatestyle)
  else:
    templateprop = properties.propfile(templatefile)
    outputpo = convertor.mergefiles(templateprop, inputprop, blankmsgstr=pot, duplicatestyle=duplicatestyle)
  if outputpo.isempty():
    return 0
  outputposrc = str(outputpo)
  outputfile.write(outputposrc)
  return 1

def main(argv=None):
  # handle command line options
  from translate.convert import convert
  formats = {"properties": ("po", convertprop), ("properties", "properties"): ("po", convertprop)}
  parser = convert.ConvertOptionParser(formats, usetemplates=True, usepots=True, description=__doc__)
  parser.add_duplicates_option()
  parser.passthrough.append("pot")
  parser.run(argv)

if __name__ == '__main__':
  main()

