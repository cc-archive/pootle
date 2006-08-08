#!/usr/bin/python

import sys
sys.path.append('../..') # in case this module is run directly
import doctest
from StringIO import StringIO

sample_template = """
Package: abook
Priority: optional
Section: mail
Installed-Size: 320
Maintainer: Gerfried Fuchs <alfie@debian.org>
Architecture: i386
Version: 0.5.5-1
Depends: libc6 (>= 2.3.5-1), libncursesw5 (>= 5.4-5), libreadline5 (>= 5.1), debconf (>= 0.5) | debconf-2.0
Filename: pool/main/a/abook/abook_0.5.5-1_i386.deb
Size: 80178
MD5sum: 14f75312ba7e6ba00c98df14900b8afc
SHA1: 55373a1b47e06d6df1a26f0484a184d16a748277
SHA256: 0fc78670343a2e6fb500e86f093a927018367b7deaf784e96c8367b9d0b1e5c1
Description: text-based ncurses address book application
 abook is a text-based ncurses address book application. It provides many
 different fields of user info. abook is designed for use with mutt, but
 can be used independently.
Enhances: mutt
Tag: interface::text-mode, role::sw:application, uitoolkit::ncurses, use::organizing, works-with::pim

Package: aap
Priority: optional
Section: devel
Installed-Size: 1052
Maintainer: Cory Dodt <corydodt@twistedmatrix.com>
Architecture: all
Version: 1.072-1
Depends: python
Suggests: aap-doc
Filename: pool/main/a/aap/aap_1.072-1_all.deb
Size: 213282
MD5sum: 7bc3d49bd89120a1f08a74af0835cb9f
SHA1: 46f52c2f13eb602792099e376da1f6afec130305
SHA256: a1aedf7ded3db8c1cfa4e2db9a3636883d73c2c20b505c7d99ef326136191eb6
Description: make-like "expert system" for building software
 A-A-P is a dependency rule-based software build system like make.  It
 eliminates many of the warts of GNU Make and can evaluate Python code
 embedded in the scripts.
"""


sample_translation = """
Package: sample
Description-md5: f00f00f00f00f00f00f00f00f00f00f0
Description-de: Beispiel
 Eines kleines Beispiel.

Package: abook
Description-md5: b3df98dd5a16801ef603bb31eff45bf6
Description-de: Ein textbasiertes Adressbuch-Programm mit ncurses
 Abook ist ein textbasiertes Adressbuch-Programm mit ncurses. Es stellt
 viele verschiedene Felder von Benutzerinformationen zur Verf\xc3\xbcgung. Abook
 wurde f\xc3\xbcr die Verwendung mit mutt entwickelt, aber kann auch unabh\xc3\xa4ngig
 davon benutzt werden.
"""



def test_parse_template():
    """Tests for parse_template().

    Let's parse some samples from a typical Packages listing:

    >>> from Pootle.storage.ddtp import parse_template
    >>> f = StringIO(sample_template)
    >>> result = parse_template(f)

    >>> for (name, md5sum, description) in result:
    ...     print '%s (MD5: %s)' % (name, md5sum)
    ...     print description
    abook (MD5: b3df98dd5a16801ef603bb31eff45bf6)
    text-based ncurses address book application
     abook is a text-based ncurses address book application. It provides many
     different fields of user info. abook is designed for use with mutt, but
     can be used independently.
    <BLANKLINE>
    aap (MD5: 709f30bc0912c0a4fd248e9ba50e6c78)
    make-like "expert system" for building software
     A-A-P is a dependency rule-based software build system like make.  It
     eliminates many of the warts of GNU Make and can evaluate Python code
     embedded in the scripts.
    <BLANKLINE>

    """


def test_parse_translation():
    """Tests for parse_translation().

    Let's parse a German translation

    >>> from Pootle.storage.ddtp import parse_translation
    >>> f = StringIO(sample_translation)

    >>> lang, result = parse_translation(f)
    >>> lang
    'de'

    >>> for (name, md5sum, description) in result:
    ...     print '%s (MD5: %s)' % (name, md5sum)
    ...     print description
    sample (MD5: f00f00f00f00f00f00f00f00f00f00f0)
    Beispiel
     Eines kleines Beispiel.
    <BLANKLINE>
    abook (MD5: b3df98dd5a16801ef603bb31eff45bf6)
    Ein textbasiertes Adressbuch-Programm mit ncurses
     Abook ist ein textbasiertes Adressbuch-Programm mit ncurses. Es stellt
     viele verschiedene Felder von Benutzerinformationen zur Verf\xc3\xbcgung. Abook
     wurde f\xc3\xbcr die Verwendung mit mutt entwickelt, aber kann auch unabh\xc3\xa4ngig
     davon benutzt werden.
    <BLANKLINE>

    """


def test_import_descriptions():
    """

    >>> from Pootle.storage.ddtp import import_descriptions
    >>> template = StringIO(sample_template)
    >>> trans = StringIO(sample_translation)

Some setup:

    >>> from Pootle.storage.memory import Module, Database
    >>> db = Database()
    >>> db.languages._items['de'] = object() # XXX breaks abstraction.
    >>> module = Module('ddtp', db)

Do the import:

    >>> import_descriptions(module, template, [trans])

Let's examine the template:

    >>> for unit in module.template:
    ...     msgid, translation = unit.trans[0]
    ...     name, md5sum = unit.automatic_comments
    ...     print '%s (MD5: %s)' % (name, md5sum)
    ...     print msgid[:20], '... -', translation and translation[:20]
    abook (MD5: b3df98dd5a16801ef603bb31eff45bf6)
    text-based ncurses a ... - None
    aap (MD5: 709f30bc0912c0a4fd248e9ba50e6c78)
    make-like "expert sy ... - None

Now let's look at the translation:

    >>> module.keys()
    ['de']

    >>> for unit in module['de']:
    ...     msgid, translation = unit.trans[0]
    ...     name, md5sum = unit.automatic_comments
    ...     print '%s (MD5: %s)' % (name, md5sum)
    ...     print msgid[:20], '... -', translation and translation[:20]
    abook (MD5: b3df98dd5a16801ef603bb31eff45bf6)
    text-based ncurses a ... - Ein textbasiertes Ad
    aap (MD5: 709f30bc0912c0a4fd248e9ba50e6c78)
    make-like "expert sy ... - None

    """


if __name__ == '__main__':
    doctest.testmod()
