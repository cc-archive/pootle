#!/usr/bin/python

import doctest

from Pootle.storage.memory import TranslationStore

sample_po = r"""# translation of foo
# Copyright (C) Foo, Inc.
# Gintautas Miliauskas <gintas@akl.lt>, 2006.
msgid ""
msgstr ""
"Project-Id-Version: foo\n"
"Last-Translator: Gintautas Miliauskas <gintas@akl.lt>\n"
"Language-Team: Lithuanian <komp_lt@konferencijos.lt>\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

#. Something
#. Anything else.
#: ../hello.c:5
msgid "Hello"
msgstr "Labas"
"""


def test_read_po():
    r"""Tests for read_po().

        >>> from Pootle.storage.po import read_po

        >>> store = TranslationStore('foo', None)
        >>> read_po(sample_po, store)

        >>> store.header.items()
        [('Project-Id-Version', u'foo'),
         ('Last-Translator', u'Gintautas Miliauskas <gintas@akl.lt>'),
         ...
         ('Content-Transfer-Encoding', u'8bit')]

        >>> for unit in store:
        ...     print unit.trans
        [(u'Hello', u'Labas')]

        >>> store[0].comments['automatic']
        [u'Something', u'Anything else.']
        >>> store[0].comments['source']
        [u'../hello.c:5']

    """


sample_po_plurals = r"""# translation of foo
# Annotation: 'owner \xc4\x85' = 'no-one \xc4\x99'
#. Plural test
msgid "One"
msgid_plural "Many"
msgstr[0] "Vienas"
msgstr[1] "Keli"
msgstr[2] "Daug"
"""

def test_read_po_plurals():
    r"""

        >>> from Pootle.storage.po import read_po

        >>> store = TranslationStore('foo', None)
        >>> read_po(sample_po_plurals, store)

        >>> for unit in store:
        ...     print unit.trans
        [(u'One', u'Vienas'), (u'Many', u'Keli'), (u'Many', u'Daug')]
        >>> print store[0].comments['automatic']
        [u'Plural test']

        >>> store[0].annotations['owner \xc4\x85']
        'no-one \xc4\x99'

    """


def test_write_po():
    r"""

    We will need a few example units:

        >>> store = TranslationStore('foo', None)
        >>> store.header['Project-Id-Version'] = 'sample'
        >>> store.header['Plural-Forms'] = 'nplurals=1; plural=0;'
        >>> store.header['POT-Creation-Date'] = '2006-08-05 22:35+0300\n'
        >>> store.header['Last-Translator'] = 'Gintautas Miliauskas <gintas@akl.lt>'

        >>> t1 = store.makeunit([('simple', 'einfach')])

        >>> t2 = store.makeunit([('spirit', 'der Geist'),
        ...                      ('spirits', 'die Geiste')])
        >>> t2.comments.add('type', 'fuzzy')
        >>> t2.comments.add('automatic', 'roboto')

        >>> store.fill([t1, t2])

    Now let's convert all this to a .po file:

        >>> from Pootle.storage.po import write_po
        >>> print write_po(store) # doctest: +REPORT_UDIFF
        msgid ""
        msgstr ""
        "Project-Id-Version: sample\n"
        "Report-Msgid-Bugs-To: \n"
        "POT-Creation-Date: 2006-08-05 22:35+0300\n"
        "PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
        "Last-Translator: Gintautas Miliauskas <gintas@akl.lt>\n"
        "Language-Team: LANGUAGE <LL@li.org>\n"
        "MIME-Version: 1.0\n"
        "Content-Type: text/plain; charset=CHARSET\n"
        "Content-Transfer-Encoding: ENCODING\n"
        "Plural-Forms: nplurals=1; plural=0;\n"
        "X-Generator: Translate Toolkit ...\n"
        <BLANKLINE>
        msgid "simple"
        msgstr "einfach"
        <BLANKLINE>
        #. roboto
        #, fuzzy
        msgid "spirit"
        msgid_plural "spirits"
        msgstr[0] "der Geist"
        msgstr[1] "die Geiste"
        <BLANKLINE>

    Annotations are also serialized as comments:

        >>> t2.annotations['foo \xc4\x85'] = 'bar \xc4\x99'
        >>> print write_po(store) # doctest: +REPORT_UDIFF, +ELLIPSIS
        msgid ""
        ...
        <BLANKLINE>
        # Annotation: 'foo \xc4\x85' = 'bar \xc4\x99'
        #. roboto
        #, fuzzy
        msgid "spirit"
        ...

    """


def test_write_po_unicode():
    r"""

        >>> store = TranslationStore('foo', None)

    We provide proper unicode:

        >>> t1 = store.makeunit([(u'm\xfcssen', u'prival\u0117ti')])
        >>> store.fill([t1])

        >>> from Pootle.storage.po import write_po

    Output is encoded to UTF-8:

        >>> lines = write_po(store).splitlines()
        >>> print lines[-2:]
        ['msgid "m\xc3\xbcssen"', 'msgstr "prival\xc4\x97ti"']

    """


if __name__ == '__main__':
    doctest.testmod(optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
