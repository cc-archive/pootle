#!/usr/bin/env python
#
# Copyright 2002-2004 Zuza Software Foundation
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
#

"""Converts OpenOffice.org exported .oo files to Gettext .po files"""

from translate.storage import po
from translate.storage import oo
from translate.misc import quote
from translate import __version__

# TODO: support using one GSI file as template, another as input (for when English is in one and translation in another)

class oo2po:
  def __init__(self, languages=None, blankmsgstr=False):
    """construct an oo2po converter for the specified languages"""
    # languages is a pair of language ids
    self.languages = languages
    self.blankmsgstr = blankmsgstr

  def makepo(self, part1, part2, key, subkey):
    """makes a po element out of a subkey of two parts"""
    thepo = po.poelement()
    thepo.sourcecomments.append("#: " + key + "." + subkey + "\n")
    text1 = getattr(part1, subkey)
    text2 = getattr(part2, subkey)
    thepo.msgid = po.quoteforpo(text1)
    thepo.msgstr = po.quoteforpo(text2)
    return thepo

  def makekey(self, ookey):
    """converts an oo key tuple into a key identifier for the po file"""
    project, sourcefile, resourcetype, groupid, localid, platform = ookey
    sourcefile = sourcefile.replace('\\','/')
    sourceparts = sourcefile.split('/')
    sourcebase = "".join(sourceparts[-1:])
    if (groupid) == 0 or len(localid) == 0:
      ooid = groupid + localid
    else:
      ooid = groupid + "." + localid
    if resourcetype:
      ooid = ooid + "." + resourcetype
    key = "%s#%s" % (sourcebase, ooid)
    return oo.normalizefilename(key)

  def convertelement(self, theoo):
    """convert an oo element into a list of po elements"""
    if self.blankmsgstr:
      if self.languages is None:
        part1 = theoo.lines[0]
      else:
        part1 = theoo.languages[self.languages[0]]
      # use a blank part2
      part2 = oo.ooline()
    else:
      if self.languages is None:
        part1 = theoo.lines[0]
        if len(theoo.lines) > 1:
          part2 = theoo.lines[1]
        else:
          part2 = oo.ooline()
      else:
        try:
          part1 = theoo.languages[self.languages[0]]
          part2 = theoo.languages[self.languages[1]]
        except KeyError, e:
          # TODO: handle this more gracefully...
          print theoo.lines[0].getkey(), "language not found: %s" % e
          return []
    key = self.makekey(part1.getkey())
    textpo = self.makepo(part1, part2, key, 'text')
    quickhelppo = self.makepo(part1, part2, key, 'quickhelptext')
    titlepo = self.makepo(part1, part2, key, 'title')
    polist = [textpo, quickhelppo, titlepo]
    return polist

  def convertfile(self, theoofile, duplicatestyle="msgid_comment"):
    """converts an entire oo file to .po format"""
    thepofile = po.pofile()
    # create a header for the file
    headerpo = thepofile.makeheader(charset="UTF-8", encoding="8bit")
    headerpo.othercomments.append("# extracted from %s\n" % theoofile.filename)
    thepofile.poelements.append(headerpo)
    # go through the oo and convert each element
    for theoo in theoofile.ooelements:
      polist = self.convertelement(theoo)
      for thepo in polist:
        thepofile.poelements.append(thepo)
    thepofile.removeblanks()
    # TODO: add a switch for duplicates...
    thepofile.removeduplicates(duplicatestyle)
    return thepofile

def convertoo(inputfile, outputfile, templates, pot=False, languages=None, duplicatestyle="msgid_comment"):
  """reads in stdin using fromfileclass, converts using convertorclass, writes to stdout"""
  fromfile = oo.oofile()
  if hasattr(inputfile, "filename"):
    fromfile.filename = inputfile.filename
  filelines = inputfile.readlines()
  fromfile.fromlines(filelines)
  if languages is not None:
    languages = [language.strip() for language in languages.split(",") if language.strip()]
  convertor = oo2po(blankmsgstr=pot, languages=languages)
  outputpo = convertor.convertfile(fromfile, duplicatestyle)
  if outputpo.isempty():
    return 0
  outputpolines = outputpo.tolines()
  outputfile.writelines(outputpolines)
  return 1

def main():
  from translate.convert import convert
  formats = {"oo":("po",convertoo)}
  # always treat the input as an archive unless it is a directory
  archiveformats = {(None, "input"): oo.oomultifile}
  parser = convert.ArchiveConvertOptionParser(formats, usepots=True, description=__doc__, archiveformats=archiveformats)
  parser.add_option("-l", "--languages", dest="languages", default=None,
    help="set languages to extract from oo file (comma-separated)", metavar="LANGUAGES")
  parser.add_option("", "--nonrecursiveinput", dest="allowrecursiveinput", default=True, action="store_false", help="don't treat the input oo as a recursive store")
  parser.add_duplicates_option()
  parser.passthrough.append("pot")
  parser.passthrough.append("languages")
  parser.run()

