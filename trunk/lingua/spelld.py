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
import win32com.client
import pythoncom
import psyco

class MSSpell:

  customdict = ""
  ignoreuppercase = False

  def __init__(self, language=None):
    pythoncom.CoInitialize()
    self.msword = win32com.client.Dispatch("Word.Application")
    self.msword.Visible = 0
    worddoc = self.msword.Documents.Add()
    self.language = language

  def closeword():
    worddoc.Close()

  def suggest(self, word):
    return self.msword.GetSpellingSuggestions(Word=word, CustomDictionary=self.customdict, IgnoreUppercase=self.ignoreuppercase, MainDictionary=self.language)

  def check(self, word):
    return self.msword.CheckSpelling(Word=word, CustomDictionary=self.customdict, IgnoreUppercase=self.ignoreuppercase, MainDictionary=self.language)
  
class SpellServerHandler(SocketServer.StreamRequestHandler):
  
  def handle(self):
    self.suggestions = {}
    self.checks = {}      
    io = self.connection.makefile("rw")
    line = io.readline()
    self.results = {}
    while line:
      if line == "\r\n" or line == ".\r\n":
        break
      command, parameters = line.decode("utf-8").split('>')
      if command.startswith('LANG'):
        for value in parameters.split():
          print "Language: %s" % value
          self.server.checker.language = value
          break
      if command.startswith('CHECK'):
        for word in parameters.split():
          print "Checking: %s" % word.encode('utf-8')
          self.request_check(word)
      if command.startswith('SUGGEST'):
        for word in parameters.split():
          print "Suggesting: %s" % word.encode('utf-8')
          self.request_suggestion(word)
      line = io.readline()
    self.report_suggestions(io)
    self.report_checks(io)
    io.close()
    self.connection.close()
  
  def request_suggestion(self, word):
    results = self.server.checker.suggest(word)
    listed = []
    for suggestion in results:
      listed.append(suggestion.Name.encode("UTF-8"))
    self.suggestions[word.encode('utf-8')] = listed

  def request_check(self, word):
    result = self.server.checker.check(word)
    self.checks[word.encode('utf-8')] = result
    
  def report_suggestions(self, output):
    for word, suggestions in self.suggestions.iteritems():
      output.write("%s:%s\r\n" % (word, ":".join(suggestions)))
    self.suggestions = None

  def report_checks(self,output):
    for word, check in self.checks.iteritems():
      output.write("%s:%s\r\n" % (word, check))
    self.checks = None
      
class SpellServer(SocketServer.TCPServer):

  def __init__(self, host="localhost", port=8000, language=None, handler=SpellServerHandler):
    self.checker = MSSpell()
    SocketServer.TCPServer.__init__(self, (host, port), handler)
    print "SpellServer started: host=%s port=%d" % (host, port)
  
def main():
  psyco.full()
  optParser = optparse.OptionParser()
  default_hostname = "localhost"
  default_port = 8000
  optParser.add_option("", "--host", action="store", dest="hostname", default=default_hostname, metavar="HOST", type="string",
      help="the spelling servers hostname (default: %s)" % default_hostname)
  optParser.add_option("-p", "--port", action="store", dest="port", default=default_port, metavar="PORT", type="int", help="the spelling servers port (default: %d)" % default_port)
  optParser.add_option("-o", "--once", action="store_true", dest="runonce", help="answer one query then exit")
  optParser.add_option("-l", "--language", action="store", dest="language", help="set the default language")
  (options, remainingArgs) = optParser.parse_args()
  server = SpellServer(options.hostname, options.port, options.language)
  if options.runonce:
    server.handle_request()
  else:
    server.serve_forever()

if __name__ == "__main__":
  main()
