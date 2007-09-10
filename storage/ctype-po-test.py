#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ctypes import *
import ctypes.util
import os

STRING = c_char_p

class po_message(Structure):
    _fields_ = []

xerror_prototype = CFUNCTYPE(None, c_int, POINTER(po_message), STRING, c_uint, c_uint, c_int, STRING)
xerror2_prototype = CFUNCTYPE(None, c_int, POINTER(po_message), STRING, c_uint, c_uint, c_int, STRING, POINTER(po_message), STRING, c_uint, c_uint, c_int, STRING)

def xerror_cb(severity, message, filename, lineno, column, multilint_p, message_text):
    print "xerror_cb", severity, message, filename, lineno, column, multilint_p, message_text

def xerror2_cb(severity, message1, filename1, lineno1, column1, nultiline_p1, message_text1, message2, filename2, lineno2, column2, multiline_p2, message_text2):
    print "xerror2_cb", severity, message1, filename1, lineno1, column1, nultiline_p1, message_text1, message2, filename2, lineno2, column2, multiline_p2, message_text2

xerror = xerror_prototype(xerror_cb)
xerror2 = xerror2_prototype(xerror2_cb)

class po_xerror_handler(Structure):
    _fields_ = [
        ('xerror', xerror_prototype),
        ('xerror2', xerror2_prototype), ]

class po_error_handler(Structure):
    _fields_ = [
    ('error', CFUNCTYPE(None, c_int, c_int, STRING)),
    ('error_at_line', CFUNCTYPE(None, c_int, c_int, STRING, c_uint, STRING)),
    ('multiline_warning', CFUNCTYPE(None, STRING, STRING)),
    ('multiline_error', CFUNCTYPE(None, STRING, STRING)),
]

# Load the library
lib_location = ctypes.util.find_library('gettextpo')
gpo = cdll.LoadLibrary(lib_location)

# Setup rettypes and argtypes
gpo.po_file_read_v3.argtypes = [STRING, POINTER(po_xerror_handler)]

gpo.po_file_domain_header.restype = STRING
gpo.po_header_field.restype = STRING
gpo.po_header_field.argtypes = [STRING, STRING]

gpo.po_filepos_file.restype = STRING

gpo.po_message_comments.restype = STRING
gpo.po_message_extracted_comments.restype = STRING
gpo.po_message_prev_msgctxt.restype = STRING
gpo.po_message_prev_msgid.restype = STRING
gpo.po_message_prev_msgid_plural.restype = STRING
gpo.po_message_msgctxt.restype = STRING
gpo.po_message_msgid.restype = STRING
gpo.po_message_msgid_plural.restype = STRING
gpo.po_message_msgstr.restype = STRING
gpo.po_message_msgstr_plural.restype = STRING

# Read the file

xerror_handler = po_xerror_handler()
xerror_handler.xerror = xerror
xerror_handler.xerror2 = xerror2

def process_po(filename):
    print "FILE: %s" % filename
    if os.path.isfile(filename):
        file = gpo.po_file_read_v3(filename, xerror_handler)
    else:
        print "file does not exist"
        return

    # Header
    header = gpo.po_file_domain_header(file, None)
    if header:
        print "is header"
        revision_date = gpo.po_header_field(header, "PO-Revision-Date")
        print "po_revision_date: %s" % revision_date

    iter = gpo.po_message_iterator(file, None)

    message = gpo.po_next_message(iter)
    while message:
        print "MSG-START"

        # Current translation content including plurals
        print "msgid: %s" % gpo.po_message_msgid(message)
        plural = gpo.po_message_msgid_plural(message)
        if plural:
            print "msgid_plural: %s" % plural 
            i = 0
            plural_trans = gpo.po_message_msgstr_plural(message, i)
            while plural_trans:
                print "msgstr[%s]: %s" % (i, plural_trans)
                i += 1
                plural_trans = gpo.po_message_msgstr_plural(message, i)
        else:
            print "msgstr: %s" % gpo.po_message_msgstr(message)
        msgctxt = gpo.po_message_msgctxt(message)
        if msgctxt:
            print "msgctxt: %s" % msgctxt

        # Comments
        trans_comment = gpo.po_message_comments(message)
        if trans_comment:
            print "translator comment: %s" % repr(trans_comment)
        extracted_comment = gpo.po_message_extracted_comments(message)
        if extracted_comment:
            print "extracted comment: %s" % repr(extracted_comment)

        # States
        if gpo.po_message_is_fuzzy(message):
            print "is fuzzy"
        if gpo.po_message_is_obsolete(message):
            print "is obsolete"
        if gpo.po_message_is_format(message, "c-format"):
            print "is c-format"

        # File locations
        i = 0
        filepos = gpo.po_message_filepos(message, i)
        while filepos:
            thefile = gpo.po_filepos_file(filepos)
            theline = gpo.po_filepos_start_line(filepos) 
            # theline = -1 then there is no line number, would be nice to make it return None
            print "location: file=%s, line=%s" % (thefile, theline)
            i += 1
            filepos = gpo.po_message_filepos(message, i)

        # Previous source text
        previous_context = gpo.po_message_prev_msgctxt(message)
        previous_source = gpo.po_message_prev_msgid(message)
        previous_source_plural = gpo.po_message_prev_msgid_plural(message)
        if previous_context: print "previous msgctxt: %s" % previous_context
        if previous_source: print "previous msgid: %s" % previous_source
        if previous_source_plural: print "previous msgid_plurals: %s" % previous_source_plural

        # Checks - needs sorting our of error handling first
        

        print "MSG-END\n"
        message = gpo.po_next_message(iter)

    # Cleanup file
    gpo.po_file_free(file)

# Scan the dirs to process PO files
for root, dirs, files in os.walk("/"):
    if ".svn" in dirs:
        dirs.remove(".svn")
    for file in files:
        if not file.endswith(".po"):
            continue
        process_po(os.path.join(root, file))


# Special empty one
process_po("does-not-exist.po")

