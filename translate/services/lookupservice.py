#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2006 Zuza Software Foundation
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

"""Server program to serve messages over XML-RPC

As this is implemented using the base classes (see storage.base), the
work is minimal to use this with any storage format that is implemented
using the base classes. Strictly speaking, only an init... function needs
to be registered."""

from translate.convert import convert
from translate.storage import tbx
from translate.storage import po

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

class lookupRequestHandler(SimpleXMLRPCRequestHandler):
    """Sets up the requested file for parsing"""
    #TODO: Parse request to see if tbx/tmx is requested,
    # or perhaps the url can specify the file to be queried
    
class lookupServer(SimpleXMLRPCServer):
    def __init__(self, addr, storage):
        """Loads the initial tbx file from the given filename"""
        SimpleXMLRPCServer.__init__(self, addr, requestHandler=lookupRequestHandler, logRequests=1)
        self.storage = storage

    def _dispatch(self, method, params):
        try:
            # All public methods must be prefixed with 'public_' so no
            # internal methods are callable.
            func = getattr(self, 'public_' + method)
        except AttributeError:
            raise Exception('no method called "%s"' % method)
        else:
            return func(*params)
    
    def internal_lookup(self, message): 
        """Could perhaps include some intelligence in future, like case trying with different casing, etc."""
        message = message.strip()
        if message == "":
            return None
        try:
            unit = self.storage.findunit(message)
        except KeyError:
            return None
        return unit
    
    def public_lookup(self, message):
        """Returns the source string of whatever was found. Keep in mind that this might not be what you want."""
        unit = self.internal_lookup(message)
        if unit:
            return str(unit)
        else:
            return ""

    def public_translate(self, message):
        """Translates the message from the storage and returns a plain string"""
        unit = self.internal_lookup(message)
        if unit and unit.target:
            return unit.target
        else:
            return ""

class lookupOptionParser(convert.ConvertOptionParser):
    """Parser that calls instantiates the lookupServer"""
    def run(self):
        """parses arguments and instantiates the server"""
        (options, args) = self.parse_args()
        options.inputformats = self.inputformats
        self.usepsyco(options)
        inputbase, inputext = self.splitinputext(options.input)
        asdf, storagebuilder = self.outputoptions[inputext, None]
        storage = storagebuilder(options.input)
        server = lookupServer((options.address, int(options.port)), storage)
        try:
            server.serve_forever()
        except:
            server.server_close()

def inittbx(inputfile, columnorder=None):
    return tbx.tbxfile(inputfile)

def initpo(inputfile, columnorder=None):
    return po.pofile(inputfile)

def initcsv(inputfile, columnorder=None):
    return csv.csvfile(inputfile, columnorder)

def main():
    formats = {"tbx": (None, inittbx), "po": (None, initpo), "csv": (None, initcsv)}
    parser = lookupOptionParser(formats, usepots=False, description=__doc__)
    parser.add_option("-a", "--address", dest="address", default="localhost",
                      help="the host to bind to")
    parser.add_option("-p", "--port", dest="port", default=1234,
                      help="the port to listen on")
    parser.add_option("-l", "--language", dest="targetlanguage", default=None, 
                      help="set target language code", metavar="LANG")
    parser.add_option("", "--source-language", dest="sourcelanguage", default='en', 
                      help="set source language code", metavar="LANG")
    parser.remove_option("--output")
    parser.remove_option("--exclude")
    parser.passthrough.append("sourcelanguage")
    parser.passthrough.append("targetlanguage")
    parser.add_option("", "--columnorder", dest="columnorder", default=None,
                      help="specify the order and position of columns for CSV (comment,source,target)")
    parser.passthrough.append("columnorder")
    parser.run()

