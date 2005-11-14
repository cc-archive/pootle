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

"""script that converts a .po file to a UTF-8 encoded .dtd file as used by mozilla
either done using a template or just using the .po file"""

import sys
from translate.storage import dtd
from translate.storage import po
from translate.misc import quote
from translate import __version__

# labelsuffixes and accesskeysuffixes are combined to accelerator notation
labelsuffixes = (".label", ".title")
accesskeysuffixes = (".accesskey", ".accessKey", ".akey")

def getlabel(unquotedstr):
  """retrieve the label from a mixed label+accesskey entity"""
  if isinstance(unquotedstr, str):
    unquotedstr = unquotedstr.decode("UTF-8")
  # mixed labels just need the & taken out
  # except that &entity; needs to be avoided...
  amppos = 0
  while amppos >= 0:
    amppos = unquotedstr.find("&",amppos)
    if amppos != -1:
      amppos += 1
      semipos = unquotedstr.find(";",amppos)
      if semipos != -1:
        if unquotedstr[amppos:semipos].isalnum():
          continue
      # otherwise, cut it out... only the first one need be changed
      # (see below to see how the accesskey is done)
      unquotedstr = unquotedstr[:amppos-1] + unquotedstr[amppos:]
      break
  return unquotedstr.encode("UTF-8")

def getaccesskey(unquotedstr):
  """retrieve the access key from a mixed label+accesskey entity"""
  if isinstance(unquotedstr, str):
    unquotedstr = unquotedstr.decode("UTF-8")
  # mixed access keys need the key extracted from after the &
  # but we must avoid proper entities i.e. &gt; etc...
  amppos = 0
  while amppos >= 0:
    amppos = unquotedstr.find("&",amppos)
    if amppos != -1:
      amppos += 1
      semipos = unquotedstr.find(";",amppos)
      if semipos != -1:
        if unquotedstr[amppos:semipos].isalnum():
          # what we have found is an entity, not a shortcut key...
          continue
      # otherwise, we found the shortcut key
      return unquotedstr[amppos].encode("UTF-8")
  # if we didn't find the shortcut key, return an empty string rather than the original string
  # this will come out as "don't have a translation for this" because the string is not changed...
  # so the string from the original dtd will be used instead
  return ""

def removeinvalidamps(entity, unquotedstr):
  """find ampersands that aren't part of an entity definition..."""
  amppos = 0
  invalidamps = []
  while amppos >= 0:
    amppos = unquotedstr.find("&",amppos)
    if amppos != -1:
      amppos += 1
      semipos = unquotedstr.find(";",amppos)
      if semipos != -1:
        checkentity = unquotedstr[amppos:semipos]
        if checkentity.replace('.','').isalnum():
          # what we have found is an entity, not a problem...
          continue
        elif checkentity[0] == '#' and checkentity[1:].isalnum():
          # what we have found is an entity, not a problem...
          continue
      # otherwise, we found a problem
      invalidamps.append(amppos-1)
  if len(invalidamps) > 0:
    print >>sys.stderr, "ampcheck failed in %s (file %s)" % (entity, sys.argv[-1])
    comp = 0
    for amppos in invalidamps:
      unquotedstr = unquotedstr[:amppos-comp] + unquotedstr[amppos-comp+1:]
      comp += 1
  return unquotedstr

def dounquotepo(thepo):
  unquotedid = po.unquotefrompo(thepo.msgid, False)
  unquotedstr = po.unquotefrompo(thepo.msgstr, False)
  return unquotedid, unquotedstr

def getmixedentities(entities):
  """returns a list of mixed .label and .accesskey entities from a list of entities"""
  mixedentities = []  # those entities which have a .label and .accesskey combined
  # search for mixed entities...
  for entity in entities:
    for labelsuffix in labelsuffixes:
      if entity.endswith(labelsuffix):
        entitybase = entity[:entity.rfind(labelsuffix)]
        # see if there is a matching accesskey, making this a mixed entity
        for akeytype in accesskeysuffixes:
          if entitybase + akeytype in entities:
            # add both versions to the list of mixed entities
            mixedentities += [entity,entitybase+akeytype]
  return mixedentities

def applytranslation(entity, thedtd, thepo, mixedentities):
  """applies the translation for entity in the po element to the dtd element"""
  # this converts the po-style string to a dtd-style string
  unquotedid, unquotedstr = dounquotepo(thepo)
  # check there aren't missing entities...
  if len(unquotedstr.strip()) == 0:
    return
  # handle mixed entities
  for labelsuffix in labelsuffixes:
    if entity.endswith(labelsuffix):
      if entity in mixedentities:
        unquotedstr = getlabel(unquotedstr)
        break
  else:
    for akeytype in accesskeysuffixes:
      if entity.endswith(akeytype):
        if entity in mixedentities:
          unquotedstr = getaccesskey(unquotedstr)
  # handle invalid left-over ampersands (usually unneeded access key shortcuts)
  unquotedstr = removeinvalidamps(entity, unquotedstr)
  # finally set the new definition in the dtd, but not if its empty
  if len(unquotedstr) > 0:
    thedtd.definition = dtd.quotefordtd(unquotedstr)

class redtd:
  """this is a convertor class that creates a new dtd based on a template using translations in a po"""
  def __init__(self, dtdfile):
    self.dtdfile = dtdfile

  def convertfile(self, pofile, includefuzzy=False):
    # translate the strings
    for thepo in pofile.poelements:
      # there may be more than one entity due to msguniq merge
      if includefuzzy or not thepo.isfuzzy():
        self.handlepoelement(thepo)
    return self.dtdfile

  def handlepoelement(self, thepo):
    entities = thepo.getsources()
    mixedentities = getmixedentities(entities)
    for entity in entities:
      if self.dtdfile.index.has_key(entity):
        # now we need to replace the definition of entity with msgstr
        thedtd = self.dtdfile.index[entity] # find the dtd
        applytranslation(entity, thedtd, thepo, mixedentities)

class po2dtd:
  """this is a convertor class that creates a new dtd file based on a po file without a template"""
  def convertcomments(self,thepo,thedtd):
    # get the entity from sourcecomments
    entitiesstr = " ".join([sourcecomment[2:].strip() for sourcecomment in thepo.sourcecomments])
    #  # entitystr, instring = quote.extract(sourcecomment, "#:","\n",None)
    #  entitiesstr += sourcecomment[2:].strip()
    entities = entitiesstr.split()
    if len(entities) > 1:
      # don't yet handle multiple entities
      thedtd.comments.append(("conversionnote",'<!-- CONVERSION NOTE - multiple entities -->\n'))
      thedtd.entity = entities[0]
    elif len(entities) == 1:
      thedtd.entity = entities[0]
    else:
      # this produces a blank entity, which doesn't write anything out
      thedtd.entity = ""

     # typecomments are for example #, fuzzy
    types = []
    for typecomment in thepo.typecomments:
      # typestr, instring = quote.extract(typecomment, "#,","\n",None)
      types.append(quote.unstripcomment(typecomment[2:]))
    for typedescr in types:
      thedtd.comments.append(("potype", typedescr+'\n'))
    # visiblecomments are for example #_ note to translator
    visibles = []
    for visiblecomment in thepo.visiblecomments:
      # visiblestr, instring = quote.extract(visiblecomment,"#_","\n",None)
      visibles.append(quote.unstripcomment(visiblecomment[2:]))
    for visible in visibles:
      thedtd.comments.append(("visible", visible+'\n'))
    # othercomments are normal e.g. # another comment
    others = []
    for othercomment in thepo.othercomments:
      # otherstr, instring = quote.extract(othercomment,"#","\n",None)
      others.append(quote.unstripcomment(othercomment[2:]))
    for other in others:
      # don't put in localization note group comments as they are artificially added
      if (other.find('LOCALIZATION NOTE') == -1) or (other.find('GROUP') == -1):
        thedtd.comments.append(("comment", other))
    # msgidcomments are special - they're actually localization notes
    for msgidcomment in thepo.msgidcomments:
      unquotedmsgidcomment = quote.extractwithoutquotes(msgidcomment,'"','"','\\',includeescapes=0)[0]
      actualnote = unquotedmsgidcomment.replace("_:","",1)
      if actualnote[-2:] == '\\n':
        actualnote = actualnote[:-2]
      locnote = quote.unstripcomment("LOCALIZATION NOTE ("+thedtd.entity+"): "+actualnote)
      thedtd.comments.append(("locnote", locnote))

  def convertstrings(self,thepo,thedtd):
    # currently let's just get the msgid back
    backslash = '\\'
    unquotedid = po.unquotefrompo(thepo.msgid, False)
    unquotedstr = po.unquotefrompo(thepo.msgstr, False)
    # choose the msgstr unless it's empty, in which case choose the msgid
    if len(unquotedstr) == 0:
      unquoted = unquotedid
    else:
      unquoted = unquotedstr
    unquoted = removeinvalidamps(thedtd.entity, unquoted)
    thedtd.definition = dtd.quotefordtd(unquoted)

  def convertelement(self,thepo):
    thedtd = dtd.dtdelement()
    self.convertcomments(thepo,thedtd)
    self.convertstrings(thepo,thedtd)
    return thedtd

  def convertfile(self, thepofile, includefuzzy=False):
    thedtdfile = dtd.dtdfile()
    self.currentgroups = []
    for thepo in thepofile.poelements:
      if includefuzzy or not thepo.isfuzzy():
        thedtd = self.convertelement(thepo)
        if thedtd is not None:
          thedtdfile.dtdelements.append(thedtd)
    return thedtdfile

def convertdtd(inputfile, outputfile, templatefile, includefuzzy=False):
  inputpo = po.pofile(inputfile)
  if templatefile is None:
    convertor = po2dtd()
  else:
    templatedtd = dtd.dtdfile(templatefile)
    convertor = redtd(templatedtd)
  outputdtd = convertor.convertfile(inputpo, includefuzzy)
  outputdtdlines = outputdtd.tolines()
  outputfile.writelines(outputdtdlines)
  return 1

if __name__ == '__main__':
  # handle command line options
  from translate.convert import convert
  formats = {"po": ("dtd", convertdtd), ("po", "dtd"): ("dtd", convertdtd)}
  parser = convert.ConvertOptionParser(formats, usetemplates=True, description=__doc__)
  parser.add_fuzzy_option()
  parser.run()

