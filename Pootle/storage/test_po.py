#!/usr/bin/python

import sys
sys.path.append('../..') # in case this module is run directly
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
        [('Hello', 'Labas')]

    """


sample_po_plurals = r"""# translation of foo
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
        [('One', 'Vienas'), ('Many', 'Keli'), ('Many', 'Daug')]
        >>> print store[0].automatic_comments
        ['#. Plural test\n']

    """


def test_write_po():
    r"""

    We will need a few example units:

        >>> store = TranslationStore('foo', None)

        >>> t1 = store.makeunit([('simple', 'einfach')])

        >>> t2 = store.makeunit([('spirit', 'der Geist'),
        ...                      ('spirits', 'die Geiste')])

        >>> t2.type_comments = ['#, fuzzy\n']
        >>> t2.automatic_comments = ['#. roboto\n']

    TODO: fix comments

        >>> store.fill([t1, t2])

    Now let's convert all this to a .po file:

        >>> from Pootle.storage.po import write_po
        >>> print write_po(store)
        msgid "simple"
        msgstr[0] "einfach"
        <BLANKLINE>
        #. roboto
        #, fuzzy
        msgid "spirit"
        msgid_plural "spirits"
        msgstr[0] "der Geist"
        msgstr[1] "die Geiste"
        <BLANKLINE>

    TODO: check Unicode support

    """


if __name__ == '__main__':
    doctest.testmod(optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
