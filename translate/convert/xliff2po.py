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
#

"""convert XLIFF localization files to Gettext PO localization files"""

from translate.storage import po
from translate.storage import xliff
from translate.misc import wStringIO

class xliff2po:
    def converttransunit(self, transunit):
        """makes a pounit from the given transunit"""
        thepo = po.pounit()

        #Header
        if transunit.getrestype() == "x-gettext-domain-header":
            thepo.source = ""
        else:
            thepo.source = transunit.source
        thepo.target = transunit.target

        #Location comments
        locations = transunit.getlocations()
        if locations:
            thepo.addlocation("%s" % " ".join(locations))

        #NOTE: Supporting both <context> and <note> tags in xliff files for comments
        #Translator comments
        trancomments = transunit.getnotes("translator")
        if trancomments:
            thepo.addnote(trancomments, origin="translator")
        
        #Automatic and Developer comments
        autocomments = transunit.getnotes("developer")
        if autocomments:
            thepo.addnote(autocomments, origin="developer")

        #See 5.6.1 of the spec. We should not check fuzzyness, but approved attribute
        if transunit.isfuzzy():
            thepo.markfuzzy(True)
        
        return thepo

    def convertstore(self, inputfile):
        """converts a .xliff file to .po format"""
        # XXX: The inputfile is converted to string because Pootle supplies
        # XXX: a PootleFile object as input which cannot be sent to PoXliffFile.
        # XXX: The better way would be to have a consistent conversion API.
        if not isinstance(inputfile, (file, wStringIO.StringIO)):
            inputfile = str(inputfile)
        XliffFile = xliff.xlifffile.parsestring(inputfile)
        thetargetfile = po.pofile()
        targetheader = thetargetfile.makeheader(charset="UTF-8", encoding="8bit")
        # TODO: support multiple files
        for transunit in XliffFile.units:
            thepo = self.converttransunit(transunit)
            thetargetfile.addunit(thepo)
        return thetargetfile

def convertxliff(inputfile, outputfile, templates):
    """reads in stdin using fromfileclass, converts using convertorclass, writes to stdout"""
    convertor = xliff2po()
    outputstore = convertor.convertstore(inputfile)
    if outputstore.isempty():
        return 0
    outputfile.write(str(outputstore))
    return 1

def main(argv=None):
    from translate.convert import convert
    formats = {"xlf":("po",convertxliff)}
    parser = convert.ConvertOptionParser(formats, usepots=True, description=__doc__)
    parser.run(argv)

