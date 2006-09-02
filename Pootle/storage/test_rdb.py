#!/usr/bin/python

import doctest


def test_Database():
    """

    Let's create an empty in-memory database:

        >>> from Pootle.storage.rdb import Database
        >>> db = Database('sqlite://')

    Let's ensure that the DB has been initialized.  The database should have
    the table 'folders':

        >>> db.engine.has_table('folders')
        True

    """


def test_Folder():
    """

    We will play around with folders a little bit.

        >>> from Pootle.storage.rdb import Database, Folder, Module

        >>> db = Database('sqlite://')

    Let's find the root folder

        >>> root = db.session.query(Folder).select_by(key='')[0]
        >>> root is db.root
        True

    The root folder has no parent folder:

        >>> root.folder is None
        True

    Let's add a module:

        >>> module = db.root.modules.add('new1')
        >>> db.session.query(Module).select_by(key='new1') == [module]
        True

    Let's test the links:

        >>> db.root.module_list == [module]
        True

        >>> module.folder is db.root
        True

    OK, that worked!  Now let's add a few subfolders one inside another.
    We'll examine attributes to make sure that all links have been set up
    properly.

        >>> rf = db.root
        >>> sub1 = rf.subfolders.add('sub1')
        >>> db.root.subfolder_list == [sub1]
        True
        >>> db.root['sub1'] is sub1
        True
        >>> db.session.query(Folder).select_by(key='sub1') == [sub1]
        True

        >>> sub1.folder is db.root
        True

    And add another subfolder:

        >>> sub2 = sub1.subfolders.add('sub2')
        >>> sub1.subfolder_list == [sub2]
        True
        >>> db.session.query(Folder).select_by(key='sub2') == [sub2]
        True

        >>> sub2.folder == sub1
        True

    And finally a module inside:

        >>> mod3 = sub2.modules.add('mod3')
        >>> db.session.query(Module).select_by(key='mod3') == [mod3]
        True

        >>> mod3.folder == sub2
        True

    """


def test_TranslationStore():
    """

    TranslationStores are stored inside modules.

        >>> from Pootle.storage.rdb import Database, Module, TranslationStore
        >>> db = Database('sqlite://')
        >>> mod = db.root.modules.add('mod')

        >>> store = mod.add('store')

    Check links:

        >>> store.key
        'store'
        >>> store.module is mod
        True
        >>> mod.store_list == [store]
        True

    """


def test_TranslationStore_find():
    """

        >>> from Pootle.storage.rdb import Database, Module, TranslationStore
        >>> db = Database('sqlite://')
        >>> mod = db.root.modules.add('mod')

        >>> store = mod.add('store')

    You can perform searches on a translation store:

        >>> unit1 = store.makeunit([('abc', 'def')])
        >>> unit2 = store.makeunit([('foo', 'barren')])
        >>> unit3 = store.makeunit([('a unit 3', 'u3')])
        >>> unit4 = store.makeunit([('a unit 4', 'u4')])
        >>> unit5 = store.makeunit([('a unit 5', 'u5')])
        >>> store.fill([unit1, unit2, unit3, unit4, unit5])
        >>> store.save()

        >>> matches = store.find('foo')
        >>> matches
        [<Pootle.storage.rdb.TranslationUnit object at ...>]
        >>> list(matches) == [unit2]
        True

        >>> for search_string in ['barren', 'bar', 'ren', 'arre',
        ...                       'bar*', '*ren', '*arre*', '*a*e*', 'a*e']:
        ...     assert store.find(search_string) == [unit2], search_string

        >>> store.find('b') == [unit1, unit2]
        True
        >>> store.find('quux') == []
        True

    Searches are not case-sensitive:

        >>> store.find('bAr') == [unit2]
        True

    You can make searches more precise:

        >>> store.find('arre', exact=True)
        []
        >>> store.find('barren', exact=True) == [unit2]
        True

    However, wildcards still work with exact=True:

        >>> store.find('bar*', exact=True) == [unit2]
        True

    You can set limits on matches:

        >>> store.find('a') == [unit1, unit2, unit3, unit4, unit5]
        True
        >>> store.find('a', limit=3) == [unit1, unit2, unit3]
        True
        >>> store.find('a', limit=2, offset=2) == [unit3, unit4]
        True

    Only the specified store will be searched:

        >>> store_b = mod.add('store_b')
        >>> unit_b = store_b.makeunit([('foo', 'baz')])
        >>> store_b.fill([unit_b])
        >>> store_b.save()

        >>> store.find('ba*') == [unit2]
        True
        >>> store_b.find('ba*') == [unit_b]
        True

    """


def test_TranslationUnit():
    """

        >>> from Pootle.storage.rdb import Database, TranslationStore
        >>> from Pootle.storage.rdb import TranslationUnit
        >>> db = Database('sqlite://')

    Let's create a store and put a few translations inside:

        >>> store = TranslationStore('store')
        >>> db.session.save(store)
        >>> unit1 = store.makeunit([('unit one', 'unit eins')])
        >>> unit2 = store.makeunit([('unit two', 'unit zwei'),
        ...                         ('unit two a', 'unit zwei a')])
        >>> store.fill([unit1, unit2])
        >>> store.save()

        >>> for unit in store:
        ...     print 'TranslationUnit %d:' % unit.index
        ...     for source, target in unit.trans:
        ...         print source, ' - ', target
        TranslationUnit 0:
        unit one  -  unit eins
        TranslationUnit 1:
        unit two  -  unit zwei
        unit two a  -  unit zwei a

    Now we will make sure that old translations are deleted when fill()
    is invoked.

        >>> unit3 = store.makeunit([('unit three', 'unit drei')])
        >>> store.fill([unit3])
        >>> store.save()

        >>> len(store.unit_list)
        1

        >>> units = store.db.session.query(TranslationUnit).select()
        >>> for unit in units:
        ...     print (unit.parent_id, ) + unit.trans[0]
        (1, 'unit three', 'unit drei')

    """


def test_interface():
    """Test conformance to the API interface.

    Poor man's alternative to zope.interface.

        >>> from Pootle.storage.api import validateModule
        >>> import Pootle.storage.rdb
        >>> validateModule(Pootle.storage.rdb, complete=True)

    """


if __name__ == '__main__':
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
