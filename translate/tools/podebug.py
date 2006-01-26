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

"""simple script to insert debug messages into po file translations"""

from translate.storage import po
from translate.misc import quote
from translate import __version__
import os
import sre

class podebug:
  def __init__(self, format=None):
    if format is None:
      self.format = ""
    else:
      self.format = format

  def openofficeignore(self, source):
    if source.startswith("Common.xcu#..Common.View.Localisation"):
      return True
    elif source.startswith("profile.lng#STR_DIR_MENU_NEW_"):
      return True
    elif source.startswith("profile.lng#STR_DIR_MENU_WIZARD_"):
      return True
    return False
                     
  def convertsource(self, thepo):
    sourceparts = []
    for sourcecomment in thepo.sourcecomments:
      sourceparts.append(sourcecomment.replace("#:","",1).strip())
    return " ".join(sourceparts)

  def convertelement(self, thepo, prefix):
    source = self.convertsource(thepo)
    if self.openofficeignore(source):
      return thepo
    msgstr = po.getunquotedstr(thepo.msgstr)
    if not msgstr:
      msgstr = po.getunquotedstr(thepo.msgid)
    msgstr = prefix + msgstr
    thepo.msgstr = [quote.quotestr(line) for line in msgstr.split('\n')]
    return thepo

  def convertfile(self, thepofile):
    filename = self.shrinkfilename(thepofile.filename)
    prefix = self.format
    for formatstr in sre.findall("%[0-9c]*[sfFbBd]", self.format):
      if formatstr.endswith("s"):
        formatted = self.shrinkfilename(thepofile.filename)
      elif formatstr.endswith("f"):
        formatted = thepofile.filename
        formatted = os.path.splitext(formatted)[0]
      elif formatstr.endswith("F"):
        formatted = thepofile.filename
      elif formatstr.endswith("b"):
        formatted = os.path.basename(thepofile.filename)
        formatted = os.path.splitext(formatted)[0]
      elif formatstr.endswith("B"):
        formatted = os.path.basename(thepofile.filename)
      elif formatstr.endswith("d"):
        formatted = os.path.dirname(thepofile.filename)
      else:
        continue
      formatoptions = formatstr[1:-1]
      if formatoptions:
        if "c" in formatoptions and formatted:
          formatted = formatted[0] + filter(lambda x: x.lower() not in "aeiou", formatted[1:])
        length = filter(str.isdigit, formatoptions)
        if length:
          formatted = formatted[:int(length)]
      prefix = prefix.replace(formatstr, formatted)
    for thepo in thepofile.units:
      if thepo.isheader() or thepo.isblank():
        continue
      thepo = self.convertelement(thepo, prefix)
    return thepofile

  def shrinkfilename(self, filename):
    if filename.startswith("." + os.sep):
      filename = filename.replace("." + os.sep, "", 1)
    dirname = os.path.dirname(filename)
    dirparts = dirname.split(os.sep)
    if not dirparts:
      dirshrunk = ""
    else:
      dirshrunk = dirparts[0][:4] + "-"
      if len(dirparts) > 1:
        dirshrunk += "".join([dirpart[0] for dirpart in dirparts[1:]]) + "-"
    baseshrunk = os.path.basename(filename)[:4]
    if "." in baseshrunk:
      baseshrunk = baseshrunk[:baseshrunk.find(".")]
    return dirshrunk + baseshrunk

def convertpo(inputfile, outputfile, templatefile, format=None):
  """reads in inputfile using po, changes to have debug strings, writes to outputfile"""
  # note that templatefile is not used, but it is required by the converter...
  inputpo = po.pofile(inputfile)
  if inputpo.isempty():
    return 0
  convertor = podebug(format=format)
  outputpo = convertor.convertfile(inputpo)
  outputfile.write(str(outputpo))
  return 1

def main():
  from translate.convert import convert
  formats = {"po":("po",convertpo)}
  parser = convert.ConvertOptionParser(formats, usepots=True, description=__doc__)
  # TODO: add documentation on format strings...
  parser.add_option("-f", "--format", dest="format", default="[%s] ", help="specify format string")
  parser.passthrough.append("format")
  parser.run()

