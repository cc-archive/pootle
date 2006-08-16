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

        >>> rootfolder = db.session.query(Folder).select(Folder.c.key=='')[0]
        >>> rootfolder is db.rootfolder
        True

    The root folder has no parent folder:

        >>> rootfolder.folder is None
        True

    Let's add a module:

        >>> module = db.rootfolder.modules.add('new1')
        >>> db.session.query(Module).select(Module.c.key=='new1') == [module]
        True

    Let's test the links:

        >>> db.rootfolder.module_list == [module]
        True
        >>> module.folder is db.rootfolder
        True

    OK, that worked!  Now let's add a few subfolders one inside another.

        >>> sub1 = db.rootfolder.subfolders.add('sub1')
        >>> db.rootfolder.subfolder_list == [sub1]
        True
        >>> db.session.query(Folder).select(Folder.c.key=='sub1') == [sub1]
        True

# XXX This does not seem to work, could be because of a self join.
#        >>> sub1.folder is db.rootfolder
#        True

        >>> sub2 = sub1.subfolders.add('sub2')
        >>> sub1.subfolder_list == [sub2]
        True
        >>> db.session.query(Folder).select(Folder.c.key=='sub2') == [sub2]
        True

#        >>> sub2.folder == sub1
#        True

        >>> mod3 = sub2.modules.add('mod3')
        >>> db.session.query(Module).select(Module.c.key=='mod3') == [mod3]
        True
        >>> mod3.folder == sub2
        True


    """


def test_interface():
    """Test conformance to the API interface.

    Poor man's alternative to zope.interface.

        >>> from Pootle.storage.api import validateModule
        >>> import Pootle.storage.rdb
        >>> validateModule(Pootle.storage.rdb, complete=True)

    """


if __name__ == '__main__':
    doctest.testmod()
