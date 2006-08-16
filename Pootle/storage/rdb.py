"""A backend that stores all data in a relational database.

Requires 
"""

from Pootle.storage.api import IDatabase
from sqlalchemy import *

DEBUG_ECHO = False # set to True to echo SQL statements


class Folder(object):
#    _interface = IFolder

    def __init__(self, db, key, folder):
        self.db = db
        self.key = key
        self.parent_id = folder.id

        self.subfolders = FolderContainer(self)
        self.modules = ModuleContainer(self)


class FolderContainer(object):

    def __init__(self, folder):
        self.folder = folder

    def add(self, key):
        folder = Folder(self.folder.db, key, self.folder)
        self.folder.db.session.save(folder)
        self.folder.db.session.flush()
        return folder


class ModuleContainer(object):
    # _interface = IMapping

    def __init__(self, folder):
        self.folder = folder

    def add(self, key):
        module = Module(self.folder.db, key, self.folder)
        self.folder.db.session.save(module)
        self.folder.db.session.flush()
        return module


class Module(object):
#    _interface = IModule

    def __init__(self, db, key, folder):
        self.db = db
        self.key = key
        self.parent_id = folder.id


class Database(object):
    """An SQL database connection."""
#    _interface = IDatabase

    id = None

    def __init__(self, engine_url):
        """Create a new connection.

        `engine_url` is an engine identifier, e.g.:
            'sqlite://' (in-memory database)
            'sqlite:////absolute/path/to/database.txt'
            'sqlite:///relative/path/to/database.txt'
            'postgres://scott:tiger@localhost:5432/mydatabase'
            'mysql://localhost/foo'
        """
        # TODO: connection pooling
        self.engine = create_engine(engine_url, echo=DEBUG_ECHO)
        self.create_tables() # TODO Don't recreate tables every time.
        self.session = create_session(bind_to=self.engine)
        self.rootfolder = Folder(self, '', self)
        self.session.save(self.rootfolder)
        self.session.flush()

    def create_tables(self):
        global metadata
        metadata.create_all(engine=self.engine)


metadata = MetaData()
folders_table = Table('folders', metadata,
    Column('id', Integer, primary_key=True),
    Column('key', String(100)),
    Column('parent_id', Integer, ForeignKey('folders.id')))
modules_table = Table('modules', metadata,
    Column('id', Integer, primary_key=True),
    Column('key', String(100)),
    Column('name', Unicode(100)),
    Column('description', Unicode(100)),
    Column('parent_id', Integer, ForeignKey('folders.id')))

# TODO: other objects

mapper(Folder, folders_table,
   properties={'subfolder_list': relation(Folder, cascade="all, delete-orphan",
                                  backref=backref('folder', uselist=False)),
               'module_list': relation(Module, cascade="all, delete-orphan",
                               backref=backref('folder', uselist=False))})
mapper(Module, modules_table)
