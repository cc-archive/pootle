#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2002-2007 Zuza Software Foundation
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

"""classes that hold units of .po files (pounit) or entire files (pofile)
gettext-style .po (or .pot) files are used in translations for KDE et al (see kbabel)"""

from translate.misc.multistring import multistring
from translate.storage import base
from translate.storage import gettextpo as gpo
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
import os
import po
import re

def quoteforpo(text):
    return po.quoteforpo(text)

def unquotefrompo(postr, joinwithlinebreak=False):
    return po.unquotefrompo(postr, joinwithlinebreak)

def encodingToUse(encoding):
    return po.encodingToUse(encoding)

class pounit(base.TranslationUnit):
    def __init__(self, source=None, encoding='utf-8', gpo_message=None):
        self._encoding = encoding
        if source or source == "":
            self._gpo_message = gpo.po_message_create()
            self.source = source
        elif gpo_message:
            self._gpo_message = gpo_message
        self.msgidcomments = []

    def setmsgid_plural(self, msgid_plural): 
        if isinstance(msgid_plural, list):
            msgid_plural = "".join(msgid_plural)
        gpo.po_message_set_msgid_plural(self._gpo_message, msgid_plural)
    msgid_plural = property(None, setmsgid_plural)

    def getsource(self):
        def remove_msgid_comments(text):
            if text.startswith('_:'):
                return text.split('\n')[1:]
            return text
        singular = remove_msgid_comments(gpo.po_message_msgid(self._gpo_message))
        if self.hasplural():
            plural = gpo.po_message_msgid_plural(self._gpo_message)
            multi = multistring([singular, plural], encoding=self._encoding)
        else:
            multi = multistring(singular, encoding=self._encoding)
        return multi

    def setsource(self, source):
        if isinstance(source, unicode):
            source = source.encode(self._encoding)
        if isinstance(source, multistring):
            source = source.strings
        if isinstance(source, list):
            gpo.po_message_set_msgid(self._gpo_message, source[0])
            if len(source) > 1:
                gpo.po_message_set_msgid_plural(self._gpo_message, source[1])
        else:
            gpo.po_message_set_msgid(self._gpo_message, source)
            
    source = property(getsource, setsource)

    def gettarget(self):
        if self.hasplural():
            plurals = []
            nplural = 0
            plural = gpo.po_message_msgstr_plural(self._gpo_message, nplural)
            while plural:
                plurals.append(plural)
                nplural += 1
                plural = gpo.po_message_msgstr_plural(self._gpo_message, nplural)
            multi = multistring(plurals, encoding=self._encoding)
        else:
            multi = multistring(gpo.po_message_msgstr(self._gpo_message) or "", encoding=self._encoding)
        return multi

    def settarget(self, target):
        if self.hasplural():
            if isinstance(target, multistring):
                target = target.strings
            elif isinstance(target, basestring):
                target = [target]
        elif isinstance(target,(dict, list)):
            if len(target) == 1:
                target = target[0]
            else:
                raise ValueError("po msgid element has no plural but msgstr has %d elements (%s)" % (len(target), target))
        if isinstance(target, list):
            for i in range(len(target)):
                if isinstance(target, unicode):
                    target = target.encode(self._encoding)
                gpo.po_message_set_msgstr_plural(self._gpo_message, i, str(target[i]))
        else:
            if isinstance(target, unicode):
               target = target.encode(self._encoding)
            gpo.po_message_set_msgstr(self._gpo_message, target)
    target = property(gettarget, settarget)

    def getnotes(self, origin=None):
        if origin == None:
            comments = gpo.po_message_comments(self._gpo_message) + \
                       gpo.po_message_extracted_comments(self._gpo_message)
        elif origin == "translator":
            comments = gpo.po_message_comments(self._gpo_message)
        elif origin in ["programmer", "developer", "source code"]:
            comments = gpo.po_message_extracted_comments(self._gpo_message)
        else:
            raise ValueError("Comment type not valid")
        # Let's drop the last newline
        return unicode(comments[:-1])

    def addnote(self, text, origin=None, position="append"):
        if not text:
            return
        oldnotes = self.getnotes(origin).encode('utf-8')
        if oldnotes:
            newnotes = oldnotes + "\n" + text
        else:
            newnotes = text
        print type(oldnotes)
        print type(newnotes)
        if origin in ["programmer", "developer", "source code"]:
            gpo.po_message_set_extracted_comments(self._gpo_message, newnotes)
        else:
            gpo.po_message_set_comments(self._gpo_message, newnotes)

    def removenotes(self):
        gpo.po_message_set_comments(self._gpo_message, "")

    def copy(self):
        newpo = self.__class__()
        newpo._gpo_message = self._gpo_message
        return newpo

    def isheader(self):
        return self.source == "" and self.target != ""

    def isblank(self):
        return len(self.source) == 0 and len(self.target == 0)

    def hasmarkedcomment(self, commentmarker):
        commentmarker = "(%s)" % commentmarker
        for comment in self.getnotes("translator").split("\n"):
            if comment.startswith(commentmarker):
                return True
        return False

    def istranslated(self):
        return super(pounit, self).istranslated() and not self.isobsolete()

    def istranslatable(self):
        return not (self.isheader() or self.isblank() or self.isobsolete())

    def isfuzzy(self):
        return gpo.po_message_is_fuzzy(self._gpo_message)

    def markfuzzy(self, present=True):
        gpo.po_message_set_fuzzy(self._gpo_message, present)

    def isreview(self):
        return self.hasmarkedcomment("review") or self.hasmarkedcomment("pofilter")

    def markreviewneeded(self, needsreview=True, explanation=None):
        if needsreview:
          reviewnote = "(review)"
          if explanation:
            reviewnote += " " + explanation
          self.addnote(reviewnote, origin="translator")
        else:
          # Strip (review) notes.
          notestring = self.getnotes(origin="translator")
          notes = notestring.split('\n')
          newnotes = []
          for note in notes:
            if not '(review)' in note:
              newnotes.append(note)
          newnotes = '\n'.join(newnotes)
          self.removenotes()
          self.addnote(newnotes, origin="translator")

    def isobsolete(self):
        return gpo.po_message_is_obsolete(self._gpo_message)

    def makeobsolete(self):
        gpo.po_message_set_obsolete(self._gpo_message, True)

    def resurrect(self):
        gpo.po_message_set_obsolete(self._gpo_message, False)

    def hasplural(self):
        return gpo.po_message_msgid_plural(self._gpo_message) is not None

    def extract_msgidcomments(self, text=None):
        """Extract KDE style msgid comments from the unit.
        
        @rtype: String
        @return: Returns the extracted msgidcomments found in this unit's msgid.
        
        """
    
        if not text:
            text = unquotefrompo(self.msgidcomments)
        return text.split('\n')[0].replace('_: ', '', 1)

    def getlocations(self):
        locations = []
        i = 0
        location = gpo.po_message_filepos(self._gpo_message, i)
        while location is not None:
            locname = gpo.po_filepos_file(location)
            locline = gpo.po_filepos_start_line(location)
            print "Dwayne %i" % locline
            # XXX this should be (size_t)(-1)
            if locline == 4294967295:
                locstring = locname
            else:
                locstring = locname + ":" + str(locline)
            locations.append(locstring)
            i =+ 1
            location = gpo.po_message_filepos(self._gpo_message, i)
        return locations

class pofile(po.pofile):
    UnitClass = pounit
    def __init__(self, inputfile=None, encoding=None, unitclass=pounit):
        self.UnitClass = unitclass
        base.TranslationStore.__init__(self, unitclass=unitclass)
        self._gpo_memory_file = None
        self._gpo_message_iterator = None
        self._encoding = encoding
        if inputfile is not None:
            self.parse(inputfile)

    def __str__(self):
        outputstring = ""
        if self._gpo_memory_file:
            outputfile = os.tmpnam()
            f = open(outputfile, "w")
            xerror = gpo.po_xerror_handler()
	    gpo.po_xerror_handler_swigregister(xerror)
            self._gpo_memory_file = gpo.po_file_write(self._gpo_memory_file, outputfile, xerror)
            f.close()
            f = open(outputfile, "r")
            outputstring = f.read()
            f.close()
            os.remove(outputfile)
        return outputstring

    def parse(self, input):
        #if hasattr(input, 'name'):
        #    self.filename = input.name
        #elif not getattr(self, 'filename', ''):
        #    self.filename = ''
        if hasattr(input, "read"):
            posrc = input.read()
            input.close()
            input = posrc
        if not os.path.isfile(input):
            # This is not a file - we write the string to a temporary file
            tmpfile = os.tmpnam()
            f = open(tmpfile, "w")
            f.write(input)
            f.close()
            input = tmpfile
        xerror = gpo.po_xerror_handler()
        self._gpo_memory_file = gpo.po_file_read(input, xerror)
        if self._gpo_memory_file is None:
            print "Error:"
        if tmpfile:
            os.remove(tmpfile)
        # Handle xerrors here
        self._header = gpo.po_file_domain_header(self._gpo_memory_file, None)
        if self._header:
            charset = gpo.po_header_field(self._header, "Content-Type")
            charset = re.search("charset=([^\\s]+)", charset)
            if charset:
                self._encoding = encodingToUse(charset.group(1))
        self._gpo_message_iterator = gpo.po_message_iterator(self._gpo_memory_file, None)
        newmessage = gpo.po_next_message(self._gpo_message_iterator)
        while newmessage:
            newunit = pounit(gpo_message=newmessage)
            self.addunit(newunit)
            newmessage = gpo.po_next_message(self._gpo_message_iterator)
#        self._free_iterator()

#    def __del__(self):
#        self._free_iterator()
#        if self._gpo_memory_file is not None:
#            gpo.po_file_free(self._gpo_memory_file)
#
#    def _free_iterator(self):
#        if self._gpo_message_iterator is not None:
#            gpo.po_message_iterator_free(self._gpo_message_iterator)
