"""A backend that stores all data in a relational database.

Requires sqlalchemy to be installed.

Supports sqlite, MySQL, PostgreSQL and other engines (see rdb.Database).

Issues:
- rollback in transactions works by not committing the changes to the
  database, however, objects already in memory are not reverted to their
  previous state -- to do that you need to use db.session.refresh()/expire()
  which is not even in the interface.
"""

import sys
from Pootle.storage.abstract import AbstractMapping
from Pootle.storage.api import IDatabase, IFolder, IMapping, IModule
from Pootle.storage.memory import LanguageInfoContainer
from sqlalchemy import *

DEBUG_ECHO = False # set to True to echo SQL statements


# ==================
# Table descriptions
# ==================

metadata = MetaData()

folders_table = Table('folders', metadata,
    Column('folder_id', Integer, primary_key=True),
    Column('parent_id', Integer, ForeignKey('folders.folder_id'),
           nullable=True),
    Column('key', String(100)),
    )

modules_table = Table('modules', metadata,
    Column('module_id', Integer, primary_key=True),
    Column('key', String(100)),
    Column('name', Unicode(100)),
    Column('description', Unicode(100)),
    Column('parent_id', Integer, ForeignKey('folders.folder_id'),
           nullable=True)
    )

stores_table = Table('stores', metadata,
    Column('store_id', Integer, primary_key=True),
    Column('parent_id', Integer, ForeignKey('modules.module_id'),
           nullable=True),
    Column('key', String(100)),
    )

units_table = Table('units', metadata,
    Column('unit_id', Integer, primary_key=True),
    Column('idx', Integer),
    Column('parent_id', Integer, ForeignKey('stores.store_id'),
           nullable=True))

trans_table = Table('trans', metadata,
    Column('trans_id', Integer, primary_key=True),
    Column('plural_idx', Integer),
    Column('parent_id', Integer, ForeignKey('units.unit_id'),
           nullable=True),
    Column('source', Unicode, nullable=False),
    Column('destination', Unicode, nullable=True))


# -------
# Helpers
# -------


class RefersToDB(object):
    """A mixin that stores the reference to the database.

    Currently we assume that there is just one instance of the database
    and store that globally.
    """

    # Static variable storing the active database.
    db = None


# -------------------
# Folders and Modules
# -------------------


class Folder(RefersToDB):
    _interface = IFolder
    _table = folders_table
    annotations = None # XXX TODO

    def statistics(self):
        pass # XXX TODO

    def __init__(self, key):
        self.key = key
        self.folder = None

    @property
    def subfolders(self):
        return FolderContainer(self)

    @property
    def modules(self):
        return ModuleContainer(self)

    def __getitem__(self, key):
        try:
            return self.subfolders[key]
        except KeyError:
            return self.modules[key]

    def __len__(self):
        return len(self.modules) + len(self.subfolders)

    def find_containers(self):
        raise NotImplementedError('FIXME')

    def find(self, substring):
        raise NotImplementedError('FIXME')


class FolderContainer(RefersToDB, AbstractMapping):
    _interface = IMapping

    def __init__(self, folder):
        self.folder = folder

    def add(self, key):
        folder = Folder(key)
        self.folder.subfolder_list.append(folder)
        self.db.save_object(self.folder)
        return folder

    def __getitem__(self, key):
        query = self.db.session.query(Folder)
        results = query.select_by(parent_id=self.folder.folder_id, key=key)
        if len(results) == 1:
            return results[0]
        else:
            raise KeyError(key)

    def keys(self):
        return [folder.key for folder in self.folder.subfolder_list]

    def __delitem__(self, key):
        raise NotImplementedError('FIXME')


class ModuleContainer(RefersToDB, AbstractMapping):
    _interface = IMapping

    def __init__(self, folder):
        self.folder = folder

    def add(self, key):
        module = Module(key)
        self.folder.module_list.append(module)
        self.db.save_object(self.folder)
        return module

    def __getitem__(self, key):
        query = self.db.session.query(Module)
        results = query.select_by(parent_id=self.folder.folder_id, key=key)
        if len(results) == 1:
            return results[0]
        else:
            raise KeyError(key)

    def keys(self):
        return [module.key for module in self.folder.module_list]

    def __delitem__(self, key):
        raise NotImplementedError('FIXME')


class Module(RefersToDB, AbstractMapping):
    _interface = IModule
    _table = modules_table
    annotations = None # XXX TODO

    @property
    def template(self):
        return self[None] # XXX

    def __init__(self, key):
        self.key = key
        self.folder = None

    def add(self, key):
        store = TranslationStore(key)
        self.store_list.append(store)
        self.db.save_object(self)
        return store

    def statistics(self):
        pass # XXX TODO

    def keys(self):
        return [store.key for store in self.store_list]

    def __getitem__(self, key):
        query = self.db.session.query(TranslationStore)
        results = query.select_by(parent_id=self.module_id, key=key)
        if len(results) == 1:
            return results[0]
        else:
            raise KeyError(key)

    def __delitem__(self, key):
        raise NotImplementedError('FIXME')

    def find(self, substring):
        raise NotImplementedError('FIXME')


# Translation store
# -----------------


class TranslationStore(RefersToDB):
    # _interface = ITranslationStore
    _table = stores_table

    def __init__(self, key):
        self.key = key
        self.module = None

    def __iter__(self):
        return iter(self.unit_list)

    def __len__(self):
        return len(self.unit_list)

    def __getitem__(self, idx):
        return self.unit_list[idx]

    def makeunit(self, trans):
        return TranslationUnit(trans)

    def fill(self, units):
        for unit in list(self.unit_list):
            self.unit_list.remove(unit)
        for i, unit in enumerate(units):
            unit.idx = i
            self.unit_list.append(unit)

    def save(self):
        self.db.save_object(self)


class TranslationUnit(RefersToDB):
    # _interface = ITranslationUnit
    _table = units_table

    @property
    def trans(self):
        return [(trans.source, trans.target)
                for trans in self.trans_list]

    def __init__(self, trans):
        for i, (source, target) in enumerate(trans):
            pair = TranslationPair(i, source, target)
            self.trans_list.append(pair)


class TranslationPair(object):
    _table = trans_table

    def __init__(self, plural_idx, source, target):
        self.plural_idx = plural_idx
        self.source = source
        self.target = target


# The database object
# ===================

class Database(object):
    """An SQL database connection."""
    _interface = IDatabase

    root = None
    languages = None
    _transaction = None

    def __init__(self, engine_url):
        """Create a new connection.

        `engine_url` is an engine identifier, e.g.:
            'sqlite://' (in-memory database)
            'sqlite:////absolute/path/to/database.txt'
            'sqlite:///relative/path/to/database.txt'
            'postgres://scott:tiger@localhost:5432/mydatabase'
            'mysql://localhost/foo'

        TODO: Currently LanguageInfoContainer is volatile, i.e., it is not
        stored inside the database.

        """
        RefersToDB.db = self # Mark itself as the active database.
        # TODO: connection pooling
        self.engine = create_engine(engine_url, echo=DEBUG_ECHO, logger=sys.stderr)
        self.create_tables() # TODO Don't recreate tables every time.
        self.session = create_session(bind_to=self.engine)
        self.root = Folder('')
        self.languages = LanguageInfoContainer(self)
        self.save_object(self.root)
        self.flush()

    def create_tables(self):
        global metadata
        metadata.create_all(engine=self.engine)

    def save_object(self, obj):
        self.session.save(obj)
        self.flush()

    def flush(self):
        self.session.flush()

    def startTransaction(self):
        self._transaction = self.session.create_transaction()
        assert self._transaction

    def rollbackTransaction(self):
        assert self._transaction, 'no active transaction'
        self._transaction.rollback()
        self._transaction = None

    def commitTransaction(self):
        assert self._transaction, 'no active transaction'
        self._transaction.commit()
        self._transaction = None


# =======
# Mappers
# =======

mapper(Folder, folders_table,
    properties={
        'subfolder_list':
            relation(Folder, private=True,
                     backref=backref("folder",
                                     foreignkey=folders_table.c.folder_id)),
        'module_list':
            relation(Module, private=True,
                     backref=backref("folder")),
    })

mapper(Module, modules_table,
    properties={
        'store_list':
            relation(TranslationStore, private=True,
                     backref=backref("module"))
    })


mapper(TranslationStore, stores_table,
    properties={
        'unit_list':
            relation(TranslationUnit, private=True,
                     order_by=units_table.c.idx,
                     backref=backref("store"))
    })


mapper(TranslationUnit, units_table,
    properties={
        'trans_list': relation(TranslationPair, private=True, lazy=False,
                               order_by=trans_table.c.plural_idx)
    })


mapper(TranslationPair, trans_table)
