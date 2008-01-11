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
from translate.storage import po
from translate.storage import properties

class prop2po:
    """convert a .properties file to a .po file for handling the translation..."""
    def convertstore(self, thepropfile, duplicatestyle="msgctxt"):
        """converts a .properties file to a .po file..."""
        thetargetfile = po.pofile()
        targetheader = thetargetfile.makeheader(charset="UTF-8", encoding="8bit", x_accelerator_marker="&")
        targetheader.addnote("extracted from %s" % thepropfile.filename, "developer")
        # we try and merge the header po with any comments at the start of the properties file
        appendedheader = 0
        waitingcomments = []
        for propunit in thepropfile.units:
            pounit = self.convertunit(propunit, "developer")
            if pounit is None:
                waitingcomments.extend(propunit.comments)
            # FIXME the storage class should not be creating blank units
            if pounit is "discard":
                continue
            if not appendedheader:
                if propunit.isblank():
                    pounit = targetheader
                else:
                    thetargetfile.addunit(targetheader)
                appendedheader = 1
            if pounit is not None:
                pounit.addnote("".join(waitingcomments).rstrip(), "developer", position="prepend")
                waitingcomments = []
                thetargetfile.addunit(pounit)
        thetargetfile.removeduplicates(duplicatestyle)
        return thetargetfile

    def mergestore(self, origpropfile, translatedpropfile, blankmsgstr=False, duplicatestyle="msgctxt"):
        """converts two .properties files to a .po file..."""
        thetargetfile = po.pofile()
        targetheader = thetargetfile.makeheader(charset="UTF-8", encoding="8bit")
        targetheader.addnote("extracted from %s, %s" % (origpropfile.filename, translatedpropfile.filename), "developer")
        translatedpropfile.makeindex()
        # we try and merge the header po with any comments at the start of the properties file
        appendedheader = 0
        waitingcomments = []
        # loop through the original file, looking at units one by one
        for origprop in origpropfile.units:
            origpo = self.convertunit(origprop, "developer")
            if origpo is None:
                waitingcomments.extend(origprop.comments)
            # FIXME the storage class should not be creating blank units
            if origpo is "discard":
                continue
            # handle the header case specially...
            if not appendedheader:
                if origprop.isblank():
                    origpo = targetheader
                else:
                    thetargetfile.addunit(targetheader)
                appendedheader = 1
            # try and find a translation of the same name...
            if origprop.name in translatedpropfile.locationindex:
                translatedprop = translatedpropfile.locationindex[origprop.name]
                # Need to check that this comment is not a copy of the developer comments
                translatedpo = self.convertunit(translatedprop, "translator")
            else:
                translatedpo = None
            # if we have a valid po unit, get the translation and add it...
            if origpo is not None:
                if translatedpo is not None and not blankmsgstr:
                    origpo.target = translatedpo.source
                origpo.addnote("".join(waitingcomments).rstrip(), "developer", position="prepend")
                waitingcomments = []
                thetargetfile.addunit(origpo)
            elif translatedpo is not None:
                print >> sys.stderr, "error converting original properties definition %s" % origprop.name
        thetargetfile.removeduplicates(duplicatestyle)
        return thetargetfile

    def convertunit(self, propunit, commenttype):
        """Converts a .properties unit to a .po unit. Returns None if empty
        or not for translation."""
        if propunit is None:
            return None
        # escape unicode
        pounit = po.pounit(encoding="UTF-8")
        if hasattr(propunit, "comments"):
            for comment in propunit.comments:
                if "DONT_TRANSLATE" in comment:
                    return "discard"
            pounit.addnote("".join(propunit.comments).rstrip(), commenttype)
        # TODO: handle multiline msgid
        if propunit.isblank():
            return None
        pounit.addlocation(propunit.name)
        pounit.source = propunit.source
        pounit.target = ""
        return pounit

def convertprop(inputfile, outputfile, templatefile, pot=False, duplicatestyle="msgctxt"):
    """reads in inputfile using properties, converts using prop2po, writes to outputfile"""
    inputstore = properties.propfile(inputfile)
    convertor = prop2po()
    if templatefile is None:
        outputstore = convertor.convertstore(inputstore, duplicatestyle=duplicatestyle)
    else:
        templatestore = properties.propfile(templatefile)
        outputstore = convertor.mergestore(templatestore, inputstore, blankmsgstr=pot, duplicatestyle=duplicatestyle)
    if outputstore.isempty():
        return 0
    outputfile.write(str(outputstore))
    return 1

def main(argv=None):
    from translate.convert import convert
    formats = {"properties": ("po", convertprop), ("properties", "properties"): ("po", convertprop)}
    parser = convert.ConvertOptionParser(formats, usetemplates=True, usepots=True, description=__doc__)
    parser.add_duplicates_option()
    parser.passthrough.append("pot")
    parser.run(argv)

if __name__ == '__main__':
    main()

