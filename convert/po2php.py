#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2002-2008 Zuza Software Foundation
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


"""convert Gettext PO localization files to PHP localization files

see: http://translate.sourceforge.net/wiki/toolkit/po2php for examples and 
usage instructions
"""

from translate.misc import quote
from translate.storage import po
from translate.storage import php

eol = "\n"

class rephp:
    def __init__(self, templatefile):
        self.templatefile = templatefile
        self.inputdict = {}

    def convertstore(self, inputstore, includefuzzy=False):
        self.inmultilinemsgid = 0
        self.inecho = 0
        self.makestoredict(inputstore, includefuzzy)
        outputlines = []
        for line in self.templatefile.readlines():
            outputstr = self.convertline(line)
            outputlines.append(outputstr)
        return outputlines

    def makestoredict(self, store, includefuzzy=False):
        '''make a dictionary of the translations'''
        for unit in store.units:
            if includefuzzy or not unit.isfuzzy():
                for location in unit.getlocations():
                    inputstring = unit.target
                    if len(inputstring.strip()) == 0:
                        inputstring = unit.source
                    self.inputdict[location] = inputstring

    def convertline(self, line):
        returnline = ""
        # handle multiline msgid if we're in one
        if self.inmultilinemsgid:
            msgid = quote.rstripeol(line).strip()
            # see if there's more
            self.inmultilinemsgid = (msgid[-2:] != "%s;" % self.quotechar)
            # if we're echoing...
            if self.inecho:
                returnline = line
        # otherwise, this could be a comment
        elif line.strip()[:2] == '//' or line.strip()[:2] == '/*':
            returnline = quote.rstripeol(line)+eol
        else:
            line = quote.rstripeol(line)
            equalspos = line.find('=')
            # if no equals, just repeat it
            if equalspos == -1:
                returnline = quote.rstripeol(line)+eol
            # otherwise, this is a definition
            else:
                # now deal with the current string...
                key = line[:equalspos].strip()
                # Calculate space around the equal sign
                prespace = line.lstrip()[line.lstrip().find(' '):equalspos]
                postspacestart = len(line[equalspos+1:])
                postspaceend = len(line[equalspos+1:].lstrip())
                postspace = line[equalspos+1:equalspos+(postspacestart-postspaceend)+1]
                self.quotechar = line[equalspos+(postspacestart-postspaceend)+1]
                print key
                if self.inputdict.has_key(key):
                    self.inecho = 0
                    value = php.phpencode(self.inputdict[key], self.quotechar)
                    if isinstance(value, str):
                        value = value.decode('utf8')
                    returnline = key + prespace + "=" + postspace + self.quotechar + value + self.quotechar + ';' + eol
                else:
                    self.inecho = 1
                    returnline = line+eol
                # no string termination at end means carry string on to next line
                if quote.rstripeol(line)[-2:] != "%s;" % self.quotechar:
                    self.inmultilinemsgid = 1
        if isinstance(returnline, unicode):
            returnline = returnline.encode('utf-8')
        return returnline

def convertphp(inputfile, outputfile, templatefile, includefuzzy=False):
    inputstore = po.pofile(inputfile)
    if templatefile is None:
        raise ValueError("must have template file for php files")
        # convertor = po2php()
    else:
        convertor = rephp(templatefile)
    outputphplines = convertor.convertstore(inputstore, includefuzzy)
    outputfile.writelines(outputphplines)
    return 1

def main(argv=None):
    # handle command line options
    from translate.convert import convert
    formats = {("po", "php"): ("php", convertphp)}
    parser = convert.ConvertOptionParser(formats, usetemplates=True, description=__doc__)
    parser.add_fuzzy_option()
    parser.run(argv)

if __name__ == '__main__':
    main()

