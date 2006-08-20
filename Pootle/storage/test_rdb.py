#!/usr/bin/python

import sys
sys.path.append('../..') # in case this module is run directly
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
        >>> mod = Module('mod')

        >>> store = mod.add('store')

    Check links:

        >>> store.key
        'store'
        >>> store.module is mod
        True
        >>> mod.store_list == [store]
        True

    """


def test_TranslationUnit():
    """

        >>> from Pootle.storage.rdb import Database, TranslationStore
        >>> from Pootle.storage.rdb import TranslationUnit
        >>> db = Database('sqlite://')

    Let's create a store and put a few translations inside:

        >>> store = TranslationStore('store')
        >>> unit1 = store.makeunit([('unit one', 'unit eins')])
        >>> unit2 = store.makeunit([('unit two', 'unit zwei'),
        ...                         ('unit two a', 'unit zwei a')])
        >>> store.fill([unit1, unit2])
        >>> store.save()

        >>> for unit in store:
        ...     print 'TranslationUnit %d:' % unit.idx
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


def test_transactions():
    """Test transaction support.

        >>> from Pootle.storage.rdb import Database, Module
        >>> db = Database('sqlite://')

        >>> module = db.root.modules.add('some_module')

    Let's start the transaction:

        >>> db.startTransaction()
        >>> module = db.session.query(Module).select()[0]
        >>> module.key
        'some_module'

    Now we change the module's key:

        >>> module.key = 'foo'

    And roll back the change:

        >>> db.rollbackTransaction()

    The module's key should not have changed.

    TODO: Work around the explicit expiration mark.

        >>> db.session.expire(module)
        >>> module.key
        u'some_module'

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
