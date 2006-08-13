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


def test_interface():
    """Test conformance to the API interface.

    Poor man's alternative to zope.interface.

        >>> from Pootle.storage.api import validateModule
        >>> import Pootle.storage.rdb
        >>> validateModule(Pootle.storage.rdb, complete=True)

    """


if __name__ == '__main__':
    doctest.testmod()
