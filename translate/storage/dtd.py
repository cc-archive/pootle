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

"""classes that hold elements of .dtd files (dtdelement) or entire files (dtdfile)
these are specific .dtd files for localisation used by mozilla
FIXME: add simple test which reads in a file and writes it out again"""

from __future__ import generators
from translate.misc import quote

class dtdelement:
  def __init__(self):
    self.comments = []
    self.incomment = 0
    self.inentity = 0

  def fromlines(self,lines):
    self.comments = []
    # make all the lists the same
    self.locfilenotes = self.comments
    self.locgroupstarts = self.comments
    self.locgroupends = self.comments
    self.locnotes = self.comments
    # self.locfilenotes = []
    # self.locgroupstarts = []
    # self.locgroupends = []
    # self.locnotes = []
    # self.comments = []
    self.entity = ''
    self.definition = ''
    linesprocessed = 0
    comment = ""
    for line in lines:
      linesprocessed += 1
      # print "line(%d,%d): " % (self.incomment,self.inentity),line[:-1]
      if not self.incomment:
        if (line.find('<!--') <> -1):
          self.incomment = 1
          self.continuecomment = 0
          # now work out the type of comment, and save it (remember we're not in the comment yet)
          (comment, dummy) = quote.extract(line,"<!--","-->",None,0)
          if comment.find('LOCALIZATION NOTE') <> -1:
            l = quote.findend(comment,'LOCALIZATION NOTE')
            while (comment[l] == ' '): l += 1
            if comment.find('FILE',l) == l:
              self.commenttype = "locfile"
            elif comment.find('BEGIN',l) == l:
              self.commenttype = "locgroupstart"
            elif comment.find('END',l) == l:
              self.commenttype = "locgroupend"
            else:
              self.commenttype = "locnote"
          else:
            # plain comment
            self.commenttype = "comment"

      if self.incomment:
        # some kind of comment
        (comment, self.incomment) = quote.extract(line,"<!--","-->",None,self.continuecomment)
        # print "comment(%d,%d): " % (self.incomment,self.continuecomment),comment
        self.continuecomment = self.incomment
        # add a end of line of this is the end of the comment
        if not self.incomment: comment += '\n'
        # depending on the type of comment (worked out at the start), put it in the right place
        # make it record the comment and type as a tuple
        commentpair = (self.commenttype,comment)
        if self.commenttype == "locfile":
          self.locfilenotes.append(commentpair)
        elif self.commenttype == "locgroupstart": 
          self.locgroupstarts.append(commentpair)
        elif self.commenttype == "locgroupend":
          self.locgroupends.append(commentpair)
        elif self.commenttype == "locnote":
          self.locnotes.append(commentpair)
        elif self.commenttype == "comment":
          self.comments.append(commentpair)
        line = line.replace(comment, "", 1)

      if not self.inentity:
        if line.find('<!ENTITY') <> -1:
          self.inentity = 1
          self.entitypart = "start"

      if self.inentity:
        if self.entitypart == "start":
          # the entity definition
          e = quote.findend(line,'<!ENTITY')
          while (line[e].isspace() and e < len(line)): e += 1
          self.entity = ''
          while (not line[e].isspace() and e < len(line)):
            self.entity += line[e]
            e += 1
          while (line[e].isspace() and e < len(line)): e += 1
          self.entitypart = "definition"
          # remember the start position and the quote character
          self.entityhelp = (e,line[e])
          self.instring = 0
        if self.entitypart == "definition":
          # actually the lines below should remember instring, rather than using it as dummy
          e = self.entityhelp[0]
          # FIXME: should we handle single quotes here? should only be double quotes
          if (self.entityhelp[1] == "'"):
            (defpart,self.instring) = quote.extract(line[e:],"'","'",None,startinstring=self.instring)
          else: # if (self.entityhelp[1] == '"'):
            (defpart,self.instring) = quote.extract(line[e:],'"','"',None,startinstring=self.instring)
          # for any following lines, start at the beginning of the line. remember the quote character
          self.entityhelp = (0,self.entityhelp[1])
          self.definition += defpart
          if not self.instring:
            self.inentity = 0
            break

    # uncomment this line to debug processing
    if 0:
      for attr in dir(self):
        r = repr(getattr(self,attr))
        if len(r) > 60: r = r[:57]+"..."
        self.comments.append(("comment","self.%s = %s" % (attr,r) ))
    return linesprocessed

  def tolines(self):
    for commenttype,comment in self.comments: yield comment
    # for f in self.locfilenotes: yield f
    # for ge in self.locgroupends: yield ge
    # for gs in self.locgroupstarts: yield gs
    # for n in self.locnotes: yield n
    if len(self.entity) > 0: 
      entityline = '<!ENTITY '+self.entity+' '+self.definition+'>'
      yield entityline+'\n'

class dtdfile:
  def __init__(self, inputfile=None):
    self.dtdelements = []
    self.filename = getattr(inputfile, 'name', '')
    if inputfile is not None:
      dtdlines = inputfile.readlines()
      self.fromlines(dtdlines)
      self.makeindex()

  def fromlines(self,lines):
    start = 0
    end = 0
    while end < len(lines):
      if (start == end): end += 1
      foundentity = 0
      while end < len(lines):
        if end >= len(lines):
          break
        if lines[end].find('<!ENTITY') > -1:
          foundentity = 1
        if foundentity and len(lines[end]) == 0:
          break
        end += 1
      # print "processing from %d to %d" % (start,end)

      linesprocessed = 1 # to initialise loop
      while linesprocessed >= 1:
        newdtd = dtdelement()
        linesprocessed = newdtd.fromlines(lines[start:end])
        # print "processed from %d to %d: %d" % (start,end,linesprocessed)
        start += linesprocessed
        if linesprocessed >= 1:
          self.dtdelements.append(newdtd)

  def tolines(self):
    lines = []
    for dtd in self.dtdelements:
      dtdlines = dtd.tolines()
      lines.extend(dtdlines)
    return lines    

  def makeindex(self):
    self.index = {}
    for dtd in self.dtdelements:
      self.index[dtd.entity] = dtd

