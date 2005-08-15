#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2005 Dwayne Bailey
#
# This file is part of the translate toolkit
#
# The translate toolkit is free software; you can redistribute it and/or modify
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

"""A server that provides access to a spell checker for validating words and receiving suggestions.
It is based on the ideas of Ikakispell but written in Python to make it multi-platform and easier
to code."""

import SocketServer
import optparse
import spellchecker

class SpellServerHandler(SocketServer.StreamRequestHandler):

  results = {}
  checker=spellconnect.BaseSpell()
  
  def handle(self):
    io = self.connection.makefile("rw")
    line = io.readline()
    self.results = {}
    while line:
      if line == "\r\n" or line == ".\r\n":
        break
      for word in line.split():
        self.request_suggestion(word)
      line = io.readline()
    self.report_suggestions(io)
    io.close()
    self.connection.close()

  def request_suggestion(self, word):
    suggestions = self.checker.suggest(word)
    self.results[word] = suggestions

  def report_suggestions(self, output):
    for word, suggestions in self.results.iteritems():
      output.write("%s\t%s\r\n" % (word, "\t".join(suggestions.split())))

class SpellServer(SocketServer.ThreadingTCPServer):

  def __init__(self, host="localhost", port=8002, handler=SpellServerHandler):
    SocketServer.TCPServer.__init__(self, (host, port), handler)
    print "SpellServer started: host=%s port=%d" % (host, port)
    
def main():
  optParser = optparse.OptionParser()
  default_hostname = "localhost"
  default_port = 8000
  optParser.add_option("", "--host", action="store", dest="hostname", default=default_hostname, metavar="HOST", type="string",
      help="the spelling servers hostname (default: %s)" % default_hostname)
  optParser.add_option("-p", "--port", action="store", dest="port", default=default_port, metavar="PORT", type="int", help="the spelling servers port (default: %d)" % default_port)
  optParser.add_option("-o", "--once", action="store_true", dest="runonce", help="answer one query then exit")
  (options, remainingArgs) = optParser.parse_args()
  server = SpellServer(options.hostname, options.port)
  if options.runonce:
    server.handle_request()
  else:
    server.serve_forever()

if __name__ == "__main__":
  main()
