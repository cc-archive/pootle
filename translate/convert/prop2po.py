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

"""simple script to convert a mozilla .properties localization file to a
gettext .pot format for translation.
does a line-by-line conversion..."""

import sys
from translate.misc import quote
from translate.storage import po
from translate.storage import properties

eol = "\n"

class prop2po:
  """convert a .properties file to a .po file for handling the translation..."""
  def convertfile(self, inputfile, outputfile):
    thepropfile = properties.propfile(inputfile)
    thepofile = po.pofile()
    headerpo = self.makeheader(thepropfile.filename)
    thepofile.poelements.append(headerpo)
    for theprop in thepropfile.propelements:
      thepo = self.convertelement(theprop)
      if thepo is not None:
        thepofile.poelements.append(thepo)
    thepofile.removeduplicates()
    outputfile.writelines(thepofile.tolines())

  def makeheader(self, filename):
    """create a header for the given filename"""
    # TODO: handle this in the po class
    headerpo = po.poelement()
    headerpo.othercomments.append("# extracted from %s\n" % filename)
    headerpo.typecomments.append("#, fuzzy\n")
    headerpo.msgid = ['""']
    headeritems = [""]
# SOME DESCRIPTIVE TITLE.
# Copyright (C) YEAR Free Software Foundation, Inc.
# FIRST AUTHOR <EMAIL@ADDRESS>, YEAR.
#
#, fuzzy
    headeritems.append("Project-Id-Version: PACKAGE VERSION\\n")
    headeritems.append("POT-Creation-Date: 2002-07-15 17:13+0100\\n")
    headeritems.append("PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n")
    headeritems.append("Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n")
    headeritems.append("Language-Team: LANGUAGE <LL@li.org>\\n")
    headeritems.append("MIME-Version: 1.0\\n")
    headeritems.append("Content-Type: text/plain; charset=CHARSET\\n")
    headeritems.append("Content-Transfer-Encoding: ENCODING\\n")
    headerpo.msgstr = [quote.quotestr(headerstr) for headerstr in headeritems]
    return headerpo

  def convertelement(self, theprop):
    """converts a .properties element to a .po element..."""
    # escape unicode
    msgid = quote.escapeunicode(theprop.msgid)
    thepo = po.poelement()
    thepo.othercomments.extend(theprop.comments)
    # TODO: handle multiline msgid
    if len(msgid) == 0:
      return None
    thepo.sourcecomments.extend("#: "+theprop.name+eol)
    thepo.msgid = [quote.quotestr(msgid, escapeescapes=1)]
    thepo.msgstr = ['""']
    return thepo

def main(inputfile, outputfile):
  convertor = prop2po()
  convertor.convertfile(inputfile, outputfile)

if __name__ == '__main__':
  # handle command line options
  try:
    import optparse
  except ImportError:
    from translate.misc import optparse
  inputformat = "properties"
  outputformat = "po"
  parser = optparse.OptionParser(usage="%prog [-i|--input-file inputfile] [-o|--output-file outputfile]")
  parser.add_option("-i", "--input-file", dest="inputfile", default=None,
                    help="read from inputfile in "+inputformat+" format", metavar="inputfile")
  parser.add_option("-o", "--output-file", dest="outputfile", default=None,
                    help="write to outputfile in "+outputformat+" format", metavar="outputfile")
  (options, args) = parser.parse_args()
  # open the appropriate files
  if options.inputfile is None:
    inputfile = sys.stdin
  else:
    inputfile = open(options.inputfile, 'r')
  if options.outputfile is None:
    outputfile = sys.stdout
  else:
    outputfile = open(options.outputfile, 'w')
  main(inputfile, outputfile)


