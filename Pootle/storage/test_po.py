#!/usr/bin/python

import sys
sys.path.append('../..') # in case this module is run directly
import doctest


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
        >>> from Pootle.storage.memory import TranslationStore

        >>> store = TranslationStore('foo', None, 'some langinfo')
        >>> read_po(sample_po, store)

        >>> for unit in store:
        ...     print unit.trans # doctest: +ELLIPSIS
        [('', '')]
        [('', 'Project-Id-Version: foo\nLast-Translator: ...\n')]
        [('Hello', 'Labas')]

    """


if __name__ == '__main__':
    doctest.testmod()
