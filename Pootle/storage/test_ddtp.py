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



def test_DDTPModule_parse_template():
    """Tests for DDTPModule.parse_template.

    Let's parse some samples from a typical Packages listing:

    >>> from Pootle.storage.ddtp import DDTPModule
    >>> module = DDTPModule(None)

    >>> f = StringIO(sample_template)
    >>> result = module.parse_template(f)

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


def test_DDTPModule_parse_translation():
    """Tests for DDTPModule.parse_translation().

    Let's parse a German translation

    >>> from Pootle.storage.ddtp import DDTPModule
    >>> module = DDTPModule(None)

    >>> f = StringIO(sample_translation)

    >>> lang, result = module.parse_translation(f)
    >>> lang
    'de'

    >>> for (name, md5sum, description) in result:
    ...     print '%s (MD5: %s)' % (name, md5sum)
    ...     print description.encode('utf-8')
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


def test_DDTPStore_load():
    """Test of DDTPStore.load()

        >>> from Pootle.storage.ddtp import DDTPModule, DDTPStore
        >>> from Pootle.storage.memory import Database
        >>> folder = Database().subfolders.add('ddtp')

    We will need to plant some information in the folder:

        >>> module = folder.modules.add('a')
        >>> store = module.add('de')

    Some drudgery for a couple examples:

        >>> units = []
        >>> def addunit(package, desc, trans, i, total, md5):
        ...     unit = store.makeunit([(desc, trans)])
        ...     comment = '%s (%s/%s)  MD5: %s' % (package, i, total, md5)
        ...     unit.automatic_comments = [comment]
        ...     units.append(unit)

        >>> addunit('kitchen', 'stool', 'der Stuhl', 1, 3, 'f00f00')
        >>> addunit('kitchen', 'table', 'der Tisch', 2, 3, 'f00f00')
        >>> addunit('kitchen', 'glass', 'das Glas', 3, 3, 'f00f00')
        >>> addunit('bedroom', 'bed', 'das Bett', 1, 1, 'faafaafaa')

        >>> store.fill(units)

    Do the import:

        >>> ddtpmodule = DDTPModule(folder)
        >>> ddtpstore = DDTPStore(ddtpmodule, 'de')
        >>> ddtpstore.load()

        >>> for package in ddtpstore.list_packages():
        ...     print package.name, ' MD5:', package.md5sum
        ...     print package.paras
        bedroom  MD5: faafaafaa
        [('bed', 'das Bett')]
        kitchen  MD5: f00f00
        [('stool', 'der Stuhl'), ('table', 'der Tisch'), ('glass', 'das Glas')]

    """


def test_DDTP_import_template():
    """

        >>> from Pootle.storage.ddtp import DDTPModule
        >>> template = StringIO(sample_template)

    Some setup:

        >>> from Pootle.storage.memory import Database
        >>> db = Database()
        >>> folder = db.subfolders.add('ddtp')
        >>> ddtpmodule = DDTPModule(folder)

    Do the import:

        >>> ddtpmodule.import_template(template)

    The strings have ended up in the template:

        >>> modulename = folder.modules.keys()[0]
        >>> module = folder.modules[modulename]

        >>> for unit in module.template:
        ...     msgid, translation = unit.trans[0]
        ...     print unit.automatic_comments
        ...     print msgid[:20], '... -', translation and translation[:20]
        ...     # doctest: +REPORT_UDIFF
        ['abook (1/2)  MD5: b3df98dd5a16801ef603bb31eff45bf6']
        text-based ncurses a ... - None
        ['abook (2/2)  MD5: b3df98dd5a16801ef603bb31eff45bf6']
        abook is a text-base ... - None
        ['aap (1/2)  MD5: 709f30bc0912c0a4fd248e9ba50e6c78']
        make-like "expert sy ... - None
        ['aap (2/2)  MD5: 709f30bc0912c0a4fd248e9ba50e6c78']
        A-A-P is a dependenc ... - None

    Now, let's import a few translations:

        >>> trans = StringIO(sample_translation)
        >>> ddtpmodule.import_translations([trans])

    Now let's look at the translation:

        >>> module.keys()
        ['de']

        >>> for unit in module['de']:
        ...     msgid, translation = unit.trans[0]
        ...     print unit.automatic_comments
        ...     print msgid[:20], '... -', translation and translation[:20]
        ['abook (1/2)  MD5: b3df98dd5a16801ef603bb31eff45bf6']
        text-based ncurses a ... - Ein textbasiertes Ad
        ['abook (2/2)  MD5: b3df98dd5a16801ef603bb31eff45bf6']
        abook is a text-base ... - Abook ist ein textba
        ['aap (1/2)  MD5: 709f30bc0912c0a4fd248e9ba50e6c78']
        make-like "expert sy ... - None
        ['aap (2/2)  MD5: 709f30bc0912c0a4fd248e9ba50e6c78']
        A-A-P is a dependenc ... - None

    """


def test_DDTPPackage_import_descriptions():
    r"""Tests for importing RFC822-style package info.

        >>> from Pootle.storage.ddtp import DDTPPackage
        >>> package = DDTPPackage('pack', '123abc')

    Simple case:

        >>> package.import_description(u'pack\n some package\n',
        ...                            u'pak\n som pakag\n')
        >>> package.paras
        [(u'pack', u'pak'), (u'some package', u'som pakag')]

    No translation:

        >>> package.import_description(u'pack\n some package\n', None)
        >>> package.paras
        [(u'pack', None), (u'some package', None)]

    Check validation:

        >>> package.import_description(u'pack\n some package\n',
        ...                            u'pak\n too\n many\n .\n pakag\n')
        Traceback (most recent call last):
            ...
        AssertionError: [u'pak', u'too many', u'pakag']

    Let's test the _split() method more carefully:

        >>> package._split('short\n one\n wrapped\n sentence.\n')
        ['short', 'one wrapped sentence.']

        >>> package._split('short\n'
        ...                ' first\n'
        ...                ' paragraph.\n'
        ...                ' .\n'
        ...                ' second paragraph.\n')
        ['short', 'first paragraph.', 'second paragraph.']

    Indented lines are not reformatted:

        >>> package._split('short\n'
        ...                ' As for this:\n'
        ...                '  leave\n'
        ...                '   it\n'
        ...                '   be,\n'
        ...                ' but unwrap\n'
        ...                ' this too.\n')
        ['short', 'As for this:\n leave\n  it\n  be, but unwrap this too.']

    TODO: Do we really want to connect "be," with "but unwrap" here?

    """


def test_DDTPPackage_export():
    r"""Tests for importing RFC822-style package info.

    A simple case:

        >>> from Pootle.storage.ddtp import DDTPPackage
        >>> package = DDTPPackage('pack', '123abc',
        ...                   [('short', 'kurz'), ('detailed', 'zugeteilt')])
        >>> print package.export('zz')
        Package: pack
        Description-md5: 123abc
        Description-zz: kurz
         zugeteilt
        <BLANKLINE>

    Test paragraph wrapping:

        >>> package.paras = [('', 'short'),
        ...                  ('', 'This is a ' + 'long ' * 30 + 'paragraph.')]
        >>> print package.export('zz')
        Package: pack
        Description-md5: 123abc
        Description-zz: short
         This is a long long long long long long long long long long long long long
         long long long long long long long long long long long long long long long
         long long paragraph.
        <BLANKLINE>

    Description
    -----------

    Formatting the description is a little problematic.  We'll test some
    corner cases:

        >>> package._export_description([" don't\n  touch\n this"])
        "  don't\n   touch\n  this"

        >>> package._export_description([" don't\n  touch\n this either," +
        ...                              " understand?" * 10])
        "  don't\n   touch\n  this either, understand? understand? understand? understand? understand? understand? understand? understand? understand? understand?"

    TODO: Is this really the behaviour we want (the documentation seems
    to imply so)?  Should we wrap the long line instead?

        >>> print package._export_description(
        ...     ["wrap " + "this line " * 10 + "\n"
        ...      " but not" + " this one" * 10 + ",\n"
        ...      "but this one" + " too" * 50])
        ... # doctest: +REPORT_UDIFF
         wrap this line this line this line this line this line this line this line
         this line this line this line
          but not this one this one this one this one this one this one this one this one this one this one,
         but this one too too too too too too too too too too too too too too too
         too too too too too too too too too too too too too too too too too too too
         too too too too too too too too too too too too too too too too

    Silly example:

        >>> print package._export_description(['', '', ''])
        <BLANKLINE>
         .
        <BLANKLINE>
         .
        <BLANKLINE>

    """


if __name__ == '__main__':
    doctest.testmod()
