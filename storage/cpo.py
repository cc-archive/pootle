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
from translate.storage import pocommon
from translate.misc import quote
from ctypes import *
import ctypes.util
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO
import os
import po
import re

STRING = c_char_p

# Structures
class po_message(Structure):
    _fields_ = []

# Function prototypes
xerror_prototype = CFUNCTYPE(None, c_int, POINTER(po_message), STRING, c_uint, c_uint, c_int, STRING)
xerror2_prototype = CFUNCTYPE(None, c_int, POINTER(po_message), STRING, c_uint, c_uint, c_int, STRING, POINTER(po_message), STRING, c_uint, c_uint, c_int, STRING)


# Structures (error handler)
class po_xerror_handler(Structure):
    _fields_ = [('xerror', xerror_prototype),
                ('xerror2', xerror2_prototype)]

class po_error_handler(Structure):
    _fields_ = [
    ('error', CFUNCTYPE(None, c_int, c_int, STRING)),
    ('error_at_line', CFUNCTYPE(None, c_int, c_int, STRING, c_uint, STRING)),
    ('multiline_warning', CFUNCTYPE(None, STRING, STRING)),
    ('multiline_error', CFUNCTYPE(None, STRING, STRING)),
]

# Callback functions for po_xerror_handler
def xerror_cb(severity, message, filename, lineno, column, multilint_p, message_text):
    print "xerror_cb", severity, message, filename, lineno, column, multilint_p, message_text
    if severity == 2:
        raise ValueError(message_text)

def xerror2_cb(severity, message1, filename1, lineno1, column1, nultiline_p1, message_text1, message2, filename2, lineno2, column2, multiline_p2, message_text2):
    print "xerror2_cb", severity, message1, filename1, lineno1, column1, nultiline_p1, message_text1, message2, filename2, lineno2, column2, multiline_p2, message_text2
    if severity == 2:
        raise ValueError(message_text)



# Load libgettextpo
lib_location = ctypes.util.find_library('gettextpo')
gpo = cdll.LoadLibrary(lib_location)


# Setup return and paramater types
# File access
gpo.po_file_read_v3.argtypes = [STRING, POINTER(po_xerror_handler)]
gpo.po_file_write_v2.argtypes = [c_int, STRING, POINTER(po_xerror_handler)]
gpo.po_file_write_v2.retype = c_int

# Header
gpo.po_file_domain_header.restype = STRING
gpo.po_header_field.restype = STRING
gpo.po_header_field.argtypes = [STRING, STRING]

# Locations (filepos)
gpo.po_filepos_file.restype = STRING
gpo.po_message_filepos.restype = c_int
gpo.po_message_filepos.argtypes = [c_int, c_int]
gpo.po_message_add_filepos.argtypes = [c_int, STRING, c_int]

# Message (get methods)
gpo.po_message_comments.restype = STRING
gpo.po_message_extracted_comments.restype = STRING
gpo.po_message_prev_msgctxt.restype = STRING
gpo.po_message_prev_msgid.restype = STRING
gpo.po_message_prev_msgid_plural.restype = STRING
gpo.po_message_is_format.restype = c_int
gpo.po_message_msgctxt.restype = STRING
gpo.po_message_msgid.restype = STRING
gpo.po_message_msgid_plural.restype = STRING
gpo.po_message_msgstr.restype = STRING
gpo.po_message_msgstr_plural.restype = STRING

# Message (set methods)
gpo.po_message_set_comments.argtypes = [c_int, STRING]
gpo.po_message_set_extracted_comments.argtypes = [c_int, STRING]
gpo.po_message_set_fuzzy.argtypes = [c_int, c_int]
gpo.po_message_set_msgctxt.argtypes = [c_int, STRING]

# Setup the po_xerror_handler
xerror_handler = po_xerror_handler()
xerror_handler.xerror = xerror_prototype(xerror_cb)
xerror_handler.xerror2 = xerror2_prototype(xerror2_cb)

def escapeforpo(text):
    return po.escapeforpo(text)

def quoteforpo(text):
    return po.quoteforpo(text)

def unquotefrompo(postr, joinwithlinebreak=False):
    return po.unquotefrompo(postr, joinwithlinebreak)

def encodingToUse(encoding):
    return po.encodingToUse(encoding)

class pounit(pocommon.pounit):
    def __init__(self, source=None, encoding='utf-8', gpo_message=None):
        self._encoding = encoding
        if not gpo_message:
            self._gpo_message = gpo.po_message_create()
        if source or source == "":
            self.source = source
            self.target = ""
        elif gpo_message:
            self._gpo_message = gpo_message

    def setmsgidcomment(self, msgidcomment):
        newsource = "_: " + msgidcomment + "\n" + self.source
        self.source = newsource
    msgidcomment = property(None, setmsgidcomment)

    def setmsgid_plural(self, msgid_plural): 
        if isinstance(msgid_plural, list):
            msgid_plural = "".join(msgid_plural)
        gpo.po_message_set_msgid_plural(self._gpo_message, msgid_plural)
    msgid_plural = property(None, setmsgid_plural)

    def getsource(self):
        def remove_msgid_comments(text):
            if not text:
                return text
            remainder = re.search(r"_: .*\n(.*)", text)
            if remainder:
                return remainder.group(1)
            else:
                return text
        multi = multistring(remove_msgid_comments(gpo.po_message_msgid(self._gpo_message)), self._encoding)
        if self.hasplural():
            pluralform = gpo.po_message_msgid_plural(self._gpo_message)
            if isinstance(pluralform, str):
                pluralform = pluralform.decode(self._encoding)
            multi.strings.append(pluralform)
        return multi

    def setsource(self, source):
        if isinstance(source, multistring):
            source = source.strings
        if isinstance(source, unicode):
            source = source.encode(self._encoding)
        if isinstance(source, list):
            gpo.po_message_set_msgid(self._gpo_message, str(source[0]))
            if len(source) > 1:
                gpo.po_message_set_msgid_plural(self._gpo_message, str(source[1]))
        else:
            gpo.po_message_set_msgid(self._gpo_message, source)
            gpo.po_message_set_msgid_plural(self._gpo_message, None)
            
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
        if isinstance(target, (dict, list)):
            i = 0
            message = gpo.po_message_msgstr_plural(self._gpo_message, i)
            while message is not None:
                gpo.po_message_set_msgstr_plural(self._gpo_message, i, None)
                i += 1
                message = gpo.po_message_msgstr_plural(self._gpo_message, i)
        if isinstance(target, list):
            for i in range(len(target)):
                targetstring = target[i]
                if isinstance(targetstring, unicode):
                    targetstring = targetstring.encode(self._encoding)
                gpo.po_message_set_msgstr_plural(self._gpo_message, i, targetstring)
        elif isinstance(target, dict):
            for i, targetstring in enumerate(target.itervalues()):
                gpo.po_message_set_msgstr_plural(self._gpo_message, i, targetstring)
        else:
            if isinstance(target, unicode):
                target = target.encode(self._encoding)
            if target is None:
                gpo.po_message_set_msgstr(self._gpo_message, "")
            else:
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
        return len(self.source) == 0 and len(self.target) == 0

    def hastypecomment(self, typecomment):
        return gpo.po_message_is_format(self._gpo_message, typecomment)

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

    def isobsolete(self):
        return gpo.po_message_is_obsolete(self._gpo_message)

    def makeobsolete(self):
        gpo.po_message_set_obsolete(self._gpo_message, True)

    def resurrect(self):
        gpo.po_message_set_obsolete(self._gpo_message, False)

    def hasplural(self):
        return gpo.po_message_msgid_plural(self._gpo_message) is not None

    def _extract_msgidcomments(self, text=None):
        """Extract KDE style msgid comments from the unit.
        
        @rtype: String
        @return: Returns the extracted msgidcomments found in this unit's msgid.
        
        """
    
        if not text:
            text = gpo.po_message_msgid(self._gpo_message)
        msgidcomment = re.search("_: (.*)\n", text)
        if msgidcomment:
            return msgidcomment.group(1)
        else:
            return ""

    def __str__(self):
        pf = pofile()
        pf.addunit(self)
        return str(pf)

    def getlocations(self):
        locations = []
        i = 0
        location = gpo.po_message_filepos(self._gpo_message, i)
        while location:
            locname = gpo.po_filepos_file(location)
            locline = gpo.po_filepos_start_line(location)
            if locline == -1:
                locstring = locname
            else:
                locstring = locname + ":" + str(locline)
            locations.append(locstring)
            i += 1
            location = gpo.po_message_filepos(self._gpo_message, i)
        return locations

    def addlocation(self, location):
        for loc in location.split():
            parts = loc.split(":")
            file = parts[0]
            if len(parts) == 2:
                line = int(parts[1])
            else:
                line = -1
            gpo.po_message_add_filepos(self._gpo_message, file, line)

    def getcontext(self):
        msgctxt = gpo.po_message_msgctxt(self._gpo_message)
        msgidcomment = self._extract_msgidcomments()
        if msgctxt:
            return msgctxt + msgidcomment
        else:
            return msgidcomment

class pofile(pocommon.pofile):
    UnitClass = pounit
    def __init__(self, inputfile=None, encoding=None, unitclass=pounit):
        self.UnitClass = unitclass
        pocommon.pofile.__init__(self, unitclass=unitclass)
        self._gpo_memory_file = None
        self._gpo_message_iterator = None
        self._encoding = encoding
        if inputfile is not None:
            self.parse(inputfile)
        else:
            self._gpo_memory_file = gpo.po_file_create()
            self._gpo_message_iterator = gpo.po_message_iterator(self._gpo_memory_file, None)

    def makeheader(self, **kwargs):
        """create a header for the given filename. arguments are specially handled, kwargs added as key: value
        pot_creation_date can be None (current date) or a value (datetime or string)
        po_revision_date can be None (form), False (=pot_creation_date), True (=now), or a value (datetime or string)"""
    
        headerpo = self.UnitClass(encoding=self._encoding)
        headerpo.markfuzzy()
        headerpo.source = ""
        headeritems = self.makeheaderdict(**kwargs)
        headeritemstring = []
        for (key, value) in headeritems.items():
            headeritemstring.append("%s: %s\n" % (key, value))
        headerpo.target = "".join(headeritemstring)
        return headerpo

    def addunit(self, unit):
        gpo.po_message_insert(self._gpo_message_iterator, unit._gpo_message)
        self.units.append(unit)

    def removeduplicates(self, duplicatestyle="merge"):
        """make sure each msgid is unique ; merge comments etc from duplicates into original"""
        msgiddict = {}
        uniqueelements = []
        # we sometimes need to keep track of what has been marked
        # TODO: this is using a list as the pos aren't hashable, but this is slow...
        markedpos = []
        def addcomment(thepo):
            thepo.msgidcomment = " ".join(thepo.getlocations())
            markedpos.append(thepo)
        for thepo in self.units:
            if thepo.isheader():
                uniqueelements.append(thepo)
                continue
            if duplicatestyle.startswith("msgid_comment"):
                msgid = thepo._extract_msgidcomments() + thepo.source
            else:
                msgid = thepo.source
            if duplicatestyle == "msgid_comment_all":
                addcomment(thepo)
                uniqueelements.append(thepo)
            elif msgid in msgiddict:
                if duplicatestyle == "merge":
                    if msgid:
                        msgiddict[msgid].merge(thepo)
                    else:
                        addcomment(thepo)
                        uniqueelements.append(thepo)
                elif duplicatestyle == "keep":
                    uniqueelements.append(thepo)
                elif duplicatestyle == "msgid_comment":
                    origpo = msgiddict[msgid]
                    if origpo not in markedpos:
                        addcomment(origpo)
                    addcomment(thepo)
                    uniqueelements.append(thepo)
                elif duplicatestyle == "msgctxt":
                    origpo = msgiddict[msgid]
                    if origpo not in markedpos:
                        gpo.po_message_set_msgctxt(origpo._gpo_message, " ".join(origpo.getlocations()))
                        markedpos.append(thepo)
                    gpo.po_message_set_msgctxt(thepo._gpo_message, " ".join(thepo.getlocations()))
                    uniqueelements.append(thepo)
            else:
                if not msgid and duplicatestyle != "keep":
                    addcomment(thepo)
                msgiddict[msgid] = thepo
                uniqueelements.append(thepo)
        self.units = uniqueelements

    def __str__(self):
        outputstring = ""
        if self._gpo_memory_file:
            outputfile = os.tmpnam()
            f = open(outputfile, "w")
            self._gpo_memory_file = gpo.po_file_write_v2(self._gpo_memory_file, outputfile, xerror_handler)
            f.close()
            f = open(outputfile, "r")
            outputstring = f.read()
            f.close()
            os.remove(outputfile)
        return outputstring

    def parse(self, input):
        if hasattr(input, 'name'):
            self.filename = input.name
        elif not getattr(self, 'filename', ''):
            self.filename = ''
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
        self._gpo_memory_file = gpo.po_file_read_v3(input, xerror_handler)
        if self._gpo_memory_file is None:
            print "Error:"
        if tmpfile:
            os.remove(tmpfile)
        # Handle xerrors here
        self._header = gpo.po_file_domain_header(self._gpo_memory_file, None)
        if self._header:
            charset = gpo.po_header_field(self._header, "Content-Type")
            if charset:
                charset = re.search("charset=([^\\s]+)", charset).group(1)
            self._encoding = encodingToUse(charset)
        self._gpo_message_iterator = gpo.po_message_iterator(self._gpo_memory_file, None)
        newmessage = gpo.po_next_message(self._gpo_message_iterator)
        while newmessage:
            newunit = pounit(gpo_message=newmessage)
            self.units.append(newunit)
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
