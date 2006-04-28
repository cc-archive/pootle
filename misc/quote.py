#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

"""string processing utilities for extracting strings with various kinds of delimiters"""

def find_all(searchin, substr):
  """returns a list of locations where substr occurs in searchin
  locations are not allowed to overlap"""
  location = 0
  locations = []
  while location != -1:
    location = searchin.find(substr, location)
    if location != -1:
      locations.append(location)
      location += len(substr)
  return locations

def extract(source,startdelim,enddelim,escape,startinstring=0):
  """Extracts a doublequote-delimited string from a string, allowing for backslash-escaping
  returns tuple of (quoted string with quotes, still in string at end)"""
  # note that this returns the quote characters as well... even internally
  instring = startinstring
  lenstart = len(startdelim)
  lenend = len(enddelim)
  lenescape = len(escape)
  startdelim_places = find_all(source, startdelim)
  if startdelim == enddelim:
    enddelim_places = startdelim_places[:]
  else:
    enddelim_places = find_all(source, enddelim)
  if escape is not None:
    escape_places = find_all(source, escape)
    last_escape_pos = -1
    # filter escaped escapes
    true_escape = False
    true_escape_places = []
    for escape_pos in escape_places:
      if escape_pos - lenescape in escape_places:
        true_escape = not true_escape
      else:
        true_escape = True
      if true_escape:
        true_escape_places.append(escape_pos)
    startdelim_places = [pos for pos in startdelim_places if pos - lenescape not in true_escape_places]
    enddelim_places = [pos + lenend for pos in enddelim_places if pos - lenescape not in true_escape_places]
  else:
    enddelim_places = [pos + lenend for pos in enddelim_places]
  # get a unique sorted list of the significant places in the string
  significant_places = dict.fromkeys([0] + startdelim_places + enddelim_places + [len(source)-1]).keys()
  significant_places.sort()
  extracted = ""
  lastpos = 0
  for pos in significant_places:
    if instring and pos in enddelim_places and lastpos != pos - lenstart:
      extracted += source[lastpos:pos]
      instring = False
      lastpos = pos
    if (not instring) and pos in startdelim_places:
      instring = True
      lastpos = pos
  if instring:
    extracted += source[lastpos:]
  return (extracted,instring)

def extractfromlines(lines,startdelim,enddelim,escape):
  """Calls extract over multiple lines, remembering whether in the string or not"""
  result = ""
  instring = 0
  for line in lines:
    (string,instring) = extract(line,startdelim,enddelim,escape,instring)
    result += string
    if not instring: break
  return result

def extractstr(source):
  "Extracts a doublequote-delimited string from a string, allowing for backslash-escaping"
  (string,instring) = extract(source,'"','"','\\')
  return string

def extractcomment(lines):
  "Extracts <!-- > XML comments from lines"
  return extractfromlines(lines,"<!--","-->",None)

def extractwithoutquotes(source,startdelim,enddelim,escape,startinstring=0,includeescapes=1):
  """Extracts a doublequote-delimited string from a string, allowing for backslash-escaping
  includeescapes can also be a function that takes the whole escaped string and returns whether to escape it"""
  instring = startinstring
  lenstart = len(startdelim)
  lenend = len(enddelim)
  lenescape = len(escape)
  startdelim_places = find_all(source, startdelim)
  if startdelim == enddelim:
    enddelim_places = startdelim_places[:]
  else:
    enddelim_places = find_all(source, enddelim)
  if escape is not None:
    escape_places = find_all(source, escape)
    last_escape_pos = -1
    # filter escaped escapes
    true_escape = False
    true_escape_places = []
    for escape_pos in escape_places:
      if escape_pos - lenescape in escape_places:
        true_escape = not true_escape
      else:
        true_escape = True
      if true_escape:
        true_escape_places.append(escape_pos)
    startdelim_places = [pos for pos in startdelim_places if pos - lenescape not in true_escape_places]
    enddelim_places = [pos + lenend for pos in enddelim_places if pos - lenescape not in true_escape_places]
  else:
    enddelim_places = [pos + lenend for pos in enddelim_places]
  # get a unique sorted list of the significant places in the string
  significant_places = dict.fromkeys([0] + startdelim_places + enddelim_places + [len(source)-1]).keys()
  significant_places.sort()
  extracted = ""
  lastpos = 0
  callable_includeescapes = callable(includeescapes)
  checkescapes = callable_includeescapes or not includeescapes
  for pos in significant_places:
    if instring and pos in enddelim_places and lastpos != pos - lenstart:
      section_start, section_end = lastpos + len(startdelim), pos - len(enddelim)
      section = source[section_start:section_end]
      if escape is not None and checkescapes:
        escape_list = [epos - section_start for epos in true_escape_places if section_start <= epos <= section_end]
        new_section = ""
        last_epos = 0
        for epos in escape_list:
          new_section += section[last_epos:epos]
          if callable_includeescapes and includeescapes(section[epos:epos+lenescape+1]):
              last_epos = epos
          else:
              last_epos = epos + lenescape
        section = new_section + section[last_epos:]
      extracted += section
      instring = False
      lastpos = pos
    if (not instring) and pos in startdelim_places:
      instring = True
      lastpos = pos
  if instring:
    section_start = lastpos + len(startdelim)
    section = source[section_start:]
    if escape is not None and not includeescapes:
      escape_list = [epos - section_start for epos in true_escape_places if section_start <= epos]
      new_section = ""
      last_epos = 0
      for epos in escape_list:
        new_section += section[last_epos:epos]
        if callable_includeescapes and includeescapes(section[epos:epos+lenescape+1]):
            last_epos = epos
        else:
            last_epos = epos + lenescape
      section = new_section + section[last_epos:]
    extracted += section
  return (extracted,instring)

def escapequotes(source, escapeescapes=0):
  "Returns the same string, with double quotes escaped with backslash"
  if escapeescapes:
    return source.replace('\\', '\\\\').replace('"', '\\"')
  else:
    return source.replace('"','\\"')

def escapesinglequotes(source):
  "Returns the same string, with single quotes doubled"
  return source.replace("'","''")

def mozillapropertiesencode(source):
  """encodes source in the escaped-unicode encoding used by mozilla .properties files"""
  output = ""
  for char in source:
    charnum = ord(char)
    if 0 <= charnum < 128:
      output += str(char)
    else:
      output += "\\u%04X" % charnum
  return output

propertyescapes = {
  # escapes that are self-escaping
  "\\": "\\", "'": "'", '"': '"',
  # control characters that we keep
  "b": "\b", "f": "\f", "t": "\t", "n": "\n", "v": "\v", "a": "\a"
  }

controlchars = {
  # the reverse of the above...
  "\b": "\\b", "\f": "\\f", "\t": "\\t", "\n": "\\n", "\v": "\\v"
  }

def escapecontrols(source):
  """escape control characters in the given string"""
  for key, value in controlchars.iteritems():
    source = source.replace(key, value)
  return source

def mozillapropertiesdecode(source):
  """decodes source from the escaped-unicode encoding used by mozilla .properties files"""
  # since the .decode("unicode-escape") routine decodes everything, and we don't want to
  # we reimplemented the algorithm from Python Objects/unicode.c in Python here
  # and modified it to retain escaped control characters
  output = u""
  s = 0
  if isinstance(source, str):
    source = source.decode("utf-8")
  def unichr2(i):
    """Returns a Unicode string of one character with ordinal 32 <= i, otherwise an escaped control character"""
    if 32 <= i:
      return unichr(i)
    elif unichr(i) in controlchars:
      # we just return the character, unescaped
      # if people want to escape them they can use escapecontrols
      return unichr(i)
    else:
      return "\\u%04x" % i
  while s < len(source):
    c = source[s]
    if c != '\\':
      output += c
      s += 1
      continue
    s += 1
    if s >= len(source):
      # this is an escape at the end of the line, which implies a continuation...
      # return the escape to inform the parser
      output += c
      continue
    c = source[s]
    s += 1
    if c == '\n': pass
    # propertyescapes lookups
    elif c in propertyescapes: output += propertyescapes[c]
    # \uXXXX escapes
    # \UXXXX escapes
    elif c in "uU":
      digits = 4
      x = 0
      for digit in range(digits):
        x <<= 4
        if s + digit >= len(source):
          digits = digit
          break
        c = source[s+digit].lower()
        if c.isdigit():
          x += ord(c) - ord('0')
        elif c in "abcdef":
          x += ord(c) - ord('a') + 10
        else:
          break
      s += digits
      output += unichr2(x)
    elif c == "N":
      if source[s] != "{":
        raise ValueError("Invalid named unicode escape")
      s += 1
      e = source.find("}", s)
      if e == -1:
        raise ValueError("Invalid named unicode escape")
      import unicodedata
      name = source[s:e]
      output += unicodedata.lookup(name)
      s = e + 1
    else:
      output += "\\" + c
  return output

def quotestr(source, escapeescapes=0):
  "Returns a doublequote-delimited quoted string, escaping double quotes with backslash"
  if isinstance(source, list):
    firstline = True
    for line in source:
      if firstline:
        newsource = '"' + escapequotes(line, escapeescapes) + '"'     
        firstline = False
      else:
        newsource = newsource + '\n' + '"' + escapequotes(line, escapeescapes) + '"'
    return newsource
  else:
    return '"' + escapequotes(source, escapeescapes) + '"'

def singlequotestr(source):
  "Returns a doublequote-delimited quoted string, escaping single quotes with themselves"
  return "'" + escapesinglequotes(source) + "'"

def eitherquotestr(source):
  "Returns a singlequote- or doublequote-delimited string, depending on what quotes it contains"
  if '"' in source:
    return singlequotestr(source)
  else:
    return quotestr(source)

def findend(string,substring):
  s = string.find(substring)
  if s <> -1:
    s += len(substring)
  return s

def rstripeol(string):
  return string.rstrip("\r\n")

def stripcomment(comment,startstring="<!--",endstring="-->"):
  cstart = comment.find(startstring)
  if cstart == -1:
    cstart = 0
  else:
    cstart += len(startstring)
  cend = comment.find(endstring,cstart)
  return comment[cstart:cend].strip()

def unstripcomment(comment,startstring="<!-- ",endstring=" -->\n"):
  return startstring+comment.strip()+endstring

def encodewithdict(unencoded, encodedict):
  """encodes certain characters in the string using an encode dictionary"""
  encoded = unencoded
  for key, value in encodedict.iteritems():
    if key in encoded:
      encoded = encoded.replace(key, value)
  return encoded

def makeutf8(d):
  """convert numbers to utf8 codes in the values of a dictionary"""
  for key, value in d.items():
    if type(value) == int:
      d[key] = unichr(value).encode('utf8')
  return d

def testcase():
  x = ' "this" " is " "a" " test!" '
  print extract(x,'"','"',None)
  print extract(x,'"','"','!')
  print extractwithoutquotes(x,'"','"',None)
  print extractwithoutquotes(x,'"','"','!')
  print extractwithoutquotes(x,'"','"','!',includeescapes=0)

if __name__ == '__main__':
  testcase()

