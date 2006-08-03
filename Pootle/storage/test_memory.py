#!/usr/bin/python

import sys
sys.path.append('../..') # in case this module is run directly
import doctest


def test_MappingMixin():
    """

        >>> from Pootle.storage.memory import MappingMixin
        >>> mm = MappingMixin()
        >>> mm._items = {'k': 'v'}
        >>> mm.keys(), mm.values(), mm.items()
        (['k'], ['v'], [('k', 'v')])
        >>> mm['k']
        'v'
        >>> len(mm)
        1

        >>> del mm['k']
        >>> mm._items
        {}
        >>> mm.add('foo')
        Traceback (most recent call last):
            ...
        NotImplementedError: override this


    """


def test_AccumStatsMixin():
    """

        >>> from Pootle.storage.memory import AccumStatsMixin, Statistics
        >>> accum = AccumStatsMixin()
        >>> class StatStub:
        ...     def __init__(self, *args):
        ...         self.args = args
        ...     def statistics(self):
        ...         return Statistics(*self.args)
        >>> accum.values = lambda: [StatStub(3, 2, 1), StatStub(8, 6, 4)]
        >>> stats = accum.statistics()

        >>> stats.total_strings, stats.translated_strings, stats.fuzzy_strings
        (11, 8, 5)

    """


def test_db():
    """

    Let's create a database:

        >>> from Pootle.storage.memory import Database
        >>> db = Database()
        >>> db.key, db.folder
        (None, None)

    """


def test_folder():
    """

    Let's create a folder:

        >>> from Pootle.storage.memory import Folder
        >>> folder = Folder('key', 'some folder')

    Let's add some things:

        >>> mod = folder.modules.add('newmodule')
        >>> fold = folder.subfolders.add('newfolder')

        >>> len(folder)
        2
        >>> folder.modules.values(), folder.subfolders.values()
        ([<Module newmodule>], [<Folder newfolder>])

        >>> folder['newmodule']
        ('module', <Module newmodule>)
        >>> folder['newfolder']
        ('folder', <Folder newfolder>)

    """


def test_Module():
    """

        >>> from Pootle.storage.memory import Module
        >>> module = Module('some', object())
        >>> module.name
        'some'

    """


def test_TranslationStore():
    """Tests for TranslationStore.

        >>> from Pootle.storage.memory import TranslationStore
        >>> coll = TranslationStore('web_ui', object())

        >>> coll.langinfo = None

        >>> tr1 = coll.makeunit([('foo', 'faa')])
        >>> tr2 = coll.makeunit([('boo', 'baa')])
        >>> tr1.store == tr2.store == coll
        True

        >>> coll.fill([tr1, tr2])
        >>> len(coll)
        2
        >>> list(coll) == [tr1, tr2]
        True
        >>> coll[:1] == [coll[0]]
        True
        >>> coll[0] == tr1
        True

    Let's check statistics:

        >>> tr1.type_comments.append('fuzzy')

        >>> stats = coll.statistics()
        >>> stats.total_strings, stats.translated_strings, stats.fuzzy_strings
        (2, 1, 1)

    """


def test_TranslationStore_translate():
    """Tests for TranslationStore.translate.

        >>> from Pootle.storage.memory import TranslationStore
        >>> coll = TranslationStore('web_ui', object())

        >>> coll.langinfo = None

        >>> tr1 = coll.makeunit([('%d chair', '%d Stuhl'),
        ...                      ('%d chairs', '%d Stuehle')])
        >>> tr2 = coll.makeunit([('foo', 'bar')])
        >>> coll.fill([tr1, tr2])

        >>> coll.translate('%d chair')
        '%d Stuhl'
        >>> coll.translate('%d chairs')
        Traceback (most recent call last):
            ...
        ValueError: no translation found for '%d chairs'
        >>> coll.translate('%d chairs', plural=1)
        '%d Stuehle'

    """


def test_unit():
    """Tests for TranslationStore.

        >>> from Pootle.storage.memory import TranslationUnit
        >>> unit = TranslationUnit(object(), [('boo', 'baa')])

        >>> unit.trans
        [('boo', 'baa')]

    """


def test_interface():
    """Test conformance to the API interface.

    Poor man's alternative to zope.interface.

        >>> from Pootle.storage.api import validateModule
        >>> import Pootle.storage.memory
        >>> validateModule(Pootle.storage.memory, complete=True)

    """


if __name__ == '__main__':
    doctest.testmod()
