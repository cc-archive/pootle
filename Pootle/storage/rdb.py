"""A backend that stores all data in a relational database.

Requires sqlalchemy to be installed.
"""

import sys
from Pootle.storage.api import IDatabase
from sqlalchemy import * # safe to use

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


# Helpers
# -------


class RefersToDB(object):
    """A mixin that stores the reference to the database.

    Currently we assume that there is just one instance of the database
    and store that globally.
    """

    db_global = None

    @property
    def db(self):
        return RefersToDB.db_global


# -------------------
# Folders and Modules
# -------------------


class Folder(RefersToDB):
#    _interface = IFolder

    def __init__(self, key):
        self.key = key
        self.folder = None

    @property
    def subfolders(self):
        return FolderContainer(self)

    @property
    def modules(self):
        return ModuleContainer(self)


class FolderContainer(RefersToDB):
    # _interface = IMapping

    def __init__(self, folder):
        self.folder = folder

    def add(self, key):
        folder = Folder(key)
        self.folder.subfolder_list.append(folder)
        self.db.save_object(self.folder)
        return folder


class ModuleContainer(RefersToDB):
    # _interface = IMapping

    def __init__(self, folder):
        self.folder = folder

    def add(self, key):
        module = Module(key)
        self.folder.module_list.append(module)
        self.db.save_object(self.folder)
        return module


class Module(RefersToDB):
#    _interface = IModule

    def __init__(self, key):
        self.key = key
        self.folder = None

    def add(self, key):
        store = TranslationStore(key)
#        store.module = self
        self.store_list.append(store)
        self.db.save_object(self)
        return store


# Translation store
# -----------------


class TranslationStore(RefersToDB):
    # _interface = ITranslationStore

    def __init__(self, key):
        self.key = key
        self.module = None


# The database object
# ===================

class Database(object):
    """An SQL database connection."""
#    _interface = IDatabase

    def __init__(self, engine_url):
        """Create a new connection.

        `engine_url` is an engine identifier, e.g.:
            'sqlite://' (in-memory database)
            'sqlite:////absolute/path/to/database.txt'
            'sqlite:///relative/path/to/database.txt'
            'postgres://scott:tiger@localhost:5432/mydatabase'
            'mysql://localhost/foo'
        """
        RefersToDB.db_global = self # Mark itself as the active database.
        # TODO: connection pooling
        self.engine = create_engine(engine_url, echo=DEBUG_ECHO, logger=sys.stderr)
        self.create_tables() # TODO Don't recreate tables every time.
        self.session = create_session(bind_to=self.engine)
        self.rootfolder = Folder('')
        self.save_object(self.rootfolder)

    def create_tables(self):
        global metadata
        metadata.create_all(engine=self.engine)

    def save_object(self, obj):
        self.session.save(obj)
        self.session.flush()


# =======
# Mappers
# =======

mapper(Folder, folders_table,
    properties={'subfolder_list':
        relation(Folder, private=True,
                 backref=backref("folder",
                                 primaryjoin=folders_table.c.parent_id==folders_table.c.folder_id,
                                 foreignkey=folders_table.c.folder_id)),
                'module_list':
        relation(Module, private=True,
# XXX This crashes the tests with a circular dependency error.
#                 backref=backref("folder",
#                                 primaryjoin=modules_table.c.parent_id==folders_table.c.folder_id,
#                                 foreignkey=folders_table.c.folder_id)
                 ),
    })

mapper(Module, modules_table,
    properties={'store_list':
        relation(TranslationStore, private=True,
                 backref=backref("module",
                                 primaryjoin=stores_table.c.parent_id==modules_table.c.module_id,
                                 foreignkey=modules_table.c.module_id))
    })


mapper(TranslationStore, stores_table)
