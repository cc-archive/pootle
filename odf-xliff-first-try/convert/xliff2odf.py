#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2004-2006 Zuza Software Foundation
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

"""convert OpenDocument (ODF) files to Gettext PO localization files"""

import sys

from translate.storage import factory

# Import from itools
import itools
import itools.handlers

import odf_shared

def make_translate_func(store):
    def translate_func(source):
        return store.findunit(source)
    return translate_func

class xliff2odf:  
    def convertstore(self, inputfile, odffile):
        """converts a file to .po format"""
        store = factory.getobject(inputfile)
        handler = itools.handlers.get_handler(odffile.name)
        try:
            translate = handler.translate
        except AttributeError:
            message = 'ERROR: The file "%s" could not be processed\n'
            sys.stderr.write(message % odffile)
            return
        return translate(make_translate_func(store), srx_handler=odf_shared.null_segmenter)

def convertodf(inputfile, outputfile, templates):
    """reads in stdin using fromfileclass, converts using convertorclass, writes to stdout"""
    convertor = xliff2odf()
    outputstore = convertor.convertstore(inputfile, templates)
    if outputstore.isempty():
        return 0
    outputfile.write(str(outputstore))
    return 1

def main(argv=None):
    from translate.convert import convert
    formats = {"xlf":("sxw", convertodf),
               "xlf":("odt", convertodf),
               "xlf":("ods", convertodf),
               "xlf":("odp", convertodf)}
    parser = convert.ConvertOptionParser(formats, usetemplates=True, description=__doc__)
    parser.run(argv)

if __name__ == '__main__':
    main()
