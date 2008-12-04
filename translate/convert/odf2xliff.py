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

"""convert OpenDocument (ODF) files to XLIFF localization files

see: http://translate.sourceforge.net/wiki/toolkit/odf2xliff for examples and
usage instructions.
"""

# Import from ttk
from translate.storage import factory

from translate.misc.contextlib import contextmanager, nested
from translate.misc.context import with_
from translate.storage import odf_io

def convertodf(inputfile, outputfile, templates, engine):
    """reads in stdin using fromfileclass, converts using convertorclass,
       writes to stdout
    """

    # Temporary hack.
    # inputfile is a Zip file, and needs to be
    # read and written as a binary file under Windows, but
    # they isn't initially in binary mode (under Windows);
    # thus, we have to reopen it as such.
    inputfile = open(inputfile.name, 'rb')

    def translate_toolkit_implementation(store):
        import cStringIO
        import zipfile

        from translate.storage.xml_extract import extract
        from translate.storage import odf_shared

        contents = odf_io.open_odf(inputfile)
        for data in contents.values():
            parse_state = extract.ParseState(odf_shared.no_translate_content_elements, 
                                             odf_shared.inline_elements)
            extract.build_store(cStringIO.StringIO(data), store, parse_state)
    
    def itools_implementation(store):
        from itools.handlers import get_handler
        from itools.gettext.po import encode_source
        import itools.odf

        filename = getattr(inputfile, 'name', 'unkown')
        handler = get_handler(filename)

        try:
            get_units = handler.get_units
        except AttributeError:
            message = 'error: the file "%s" could not be processed'
            raise AttributeError, message % filename

        # Make the XLIFF file
        for source, context, line in get_units():
            source = encode_source(source)
            unit = store.UnitClass(source)
            store.addunit(unit)

    @contextmanager
    def store_context():
        store = factory.getobject(outputfile)
        yield store
        store.save()

    def with_block(store):
        if engine == "toolkit":
            translate_toolkit_implementation(store)
        else:
            itools_implementation(store)
    
    with_(store_context(), with_block)
    return True


def main(argv=None):
    def add_options(parser):
        parser.add_option("", "--engine", dest="engine", default="toolkit",
                          type="choice", choices=["toolkit", "itools"],
                          help="""Choose whether itools (--engine=itools) or the translate toolkit (--engine=toolkit)
                          should be used as the engine to convert an ODF file to an XLIFF file.""")
        parser.passthrough = ['engine']
        return parser
    
    from translate.convert import convert
    formats = {"sxw": ("xlf", convertodf),
               "odt": ("xlf", convertodf),
               "ods": ("xlf", convertodf),
               "odp": ("xlf", convertodf)}
    parser = convert.ConvertOptionParser(formats, description=__doc__)
    add_options(parser)
    parser.run(argv)

if __name__ == '__main__':
    main()
