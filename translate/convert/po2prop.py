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


"""convert Gettext PO localization files to Java/Mozilla .properties files

see: http://translate.sourceforge.net/wiki/toolkit/po2prop for examples and
usage instructions
"""

from translate.misc import quote
from translate.storage import po
from translate.storage import properties

eol = "\n"


class reprop:

    def __init__(self, templatefile, personality, encoding):
        self.personality = properties.get_dialect(personality)
        self.encoding = encoding
        if self.encoding is None:
            self.encoding = self.personality.default_encoding
        self.templatefile = templatefile
        self.inputdict = {}

    def convertstore(self, inputstore, includefuzzy=False):
        self.inmultilinemsgid = False
        self.inecho = False
        self.makestoredict(inputstore, includefuzzy)
        outputlines = []
        # Readlines doesn't work for UTF-16, we read() and splitlines(keepends) instead
        content = self.templatefile.read().decode(self.encoding)
        for line in content.splitlines(True):
            outputstr = self.convertline(line)
            outputlines.append(outputstr)
        return outputlines

    def makestoredict(self, store, includefuzzy=False):
        # make a dictionary of the translations
        for unit in store.units:
            if includefuzzy or not unit.isfuzzy():
                # there may be more than one entity due to msguniq merge
                for entity in unit.getlocations():
                    propstring = unit.target
                    # NOTE: triple-space as a string means leave it
                    # empty (special signal)
                    if len(propstring.strip()) == 0 and propstring != "   ":
                        propstring = unit.source
                    self.inputdict[entity] = propstring

    def convertline(self, line):
        returnline = u""
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
            line = quote.rstripeol(line)
            delimiter_char, delimiter_pos = self.personality.find_delimiter(line)
            if quote.rstripeol(line)[-1:] == '\\':
                self.inmultilinemsgid = True
            if delimiter_pos == -1:
                key = self.personality.key_strip(line)
                delimiter = " %s " % self.personality.delimiters[0]
            else:
                key = self.personality.key_strip(line[:delimiter_pos])
                # Calculate space around the equal sign
                prespace = line[line.find(' ', len(key)):delimiter_pos]
                postspacestart = len(line[delimiter_pos+1:])
                postspaceend = len(line[delimiter_pos+1:].lstrip())
                postspace = line[delimiter_pos+1:delimiter_pos+(postspacestart-postspaceend)+1]
                delimiter = prespace + delimiter_char + postspace
            if key in self.inputdict:
                self.inecho = False
                value = self.inputdict[key]
                assert isinstance(value, unicode)
                returnline = "%(key)s%(del)s%(value)s%(term)s%(eol)s" % \
                     {"key": "%s%s%s" % (self.personality.key_wrap_char,
                                         key,
                                         self.personality.key_wrap_char),
                      "del": delimiter,
                      "value": "%s%s%s" % (self.personality.value_wrap_char,
                                           self.personality.encode(value),
                                           self.personality.value_wrap_char),
                      "term": self.personality.pair_terminator,
                      "eol": eol,
                     }
            else:
                self.inecho = True
                returnline = line + eol
        assert isinstance(returnline, unicode)
        returnline = returnline.encode(self.encoding)
        return returnline


def convertstrings(inputfile, outputfile, templatefile, personality="strings",
                       includefuzzy=False, encoding=None):
    """.strings specific convertor function"""
    return convertprop(inputfile, outputfile, templatefile,
                       personality="strings", includefuzzy=includefuzzy,
                       encoding=encoding)


def convertmozillaprop(inputfile, outputfile, templatefile,
                       includefuzzy=False):
    """Mozilla specific convertor function"""
    return convertprop(inputfile, outputfile, templatefile,
                       personality="mozilla", includefuzzy=includefuzzy)


def convertprop(inputfile, outputfile, templatefile, personality="java",
                includefuzzy=False, encoding=None):
    inputstore = po.pofile(inputfile)
    if templatefile is None:
        raise ValueError("must have template file for properties files")
        # convertor = po2prop()
    else:
        convertor = reprop(templatefile, personality, encoding)
    outputproplines = convertor.convertstore(inputstore, includefuzzy)
    outputfile.writelines(outputproplines)
    return 1

formats = {
    ("po", "properties"): ("properties", convertprop),
    ("po", "lang"): ("lang", convertprop),
    ("po", "strings"): ("strings", convertstrings),
}


def main(argv=None):
    # handle command line options
    from translate.convert import convert
    parser = convert.ConvertOptionParser(formats, usetemplates=True,
                                         description=__doc__)
    parser.add_option("", "--personality", dest="personality",
            default=properties.default_dialect, type="choice",
            choices=properties.dialects.keys(),
            help="override the input file format: %s (for .properties files, default: %s)" %
                 (", ".join(properties.dialects.iterkeys()),
                  properties.default_dialect),
            metavar="TYPE")
    parser.add_option("", "--encoding", dest="encoding", default=None,
            help="override the encoding set by the personality",
            metavar="ENCODING")
    parser.add_fuzzy_option()
    parser.passthrough.append("personality")
    parser.passthrough.append("encoding")
    parser.run(argv)

if __name__ == '__main__':
    main()
