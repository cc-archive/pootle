"""A backend that stores all data in a relational database.

Requires sqlalchemy to be installed.

Supports sqlite, MySQL, PostgreSQL and other engines (see rdb.Database).
"""

import sys
from Pootle.storage.abstract import (
    AbstractMapping, SearchableFolder, SearchableModule)
from Pootle.storage.api import IDatabase, IFolder, IMapping, IModule
from Pootle.storage.api import ITranslationStore, ITranslationUnit
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
    Column('key', String),
    )

modules_table = Table('modules', metadata,
    Column('module_id', Integer, primary_key=True),
    Column('key', String),
    Column('name', Unicode),
    Column('description', Unicode, nullable=True),
    Column('parent_id', Integer, ForeignKey('folders.folder_id'),
           nullable=True)
    )

stores_table = Table('stores', metadata,
    Column('store_id', Integer, primary_key=True),
    Column('parent_id', Integer, ForeignKey('modules.module_id'),
           nullable=True),
    Column('key', String),
    )

headers_table = Table('headers', metadata,
    Column('header_id', Integer, primary_key=True),
    Column('parent_id', Integer, ForeignKey('stores.store_id'),
           nullable=True),
    Column('key', String),
    Column('value', Unicode)
    )

units_table = Table('units', metadata,
    Column('unit_id', Integer, primary_key=True),
    Column('idx', Integer),
    Column('parent_id', Integer, ForeignKey('stores.store_id'),
           nullable=True))

store_annotations_table = Table('store_annotations', metadata,
    Column('annotation_id', Integer, primary_key=True),
    Column('parent_id', Integer, ForeignKey('stores.store_id'),
           nullable=True),
    Column('key', String),
    Column('value', String)
    )

unit_annotations_table = Table('unit_annotations', metadata,
    Column('annotation_id', Integer, primary_key=True),
    Column('parent_id', Integer, ForeignKey('units.unit_id'),
           nullable=True),
    Column('key', String),
    Column('value', String)
    )

trans_table = Table('trans', metadata,
    Column('trans_id', Integer, primary_key=True),
    Column('plural_idx', Integer),
    Column('parent_id', Integer, ForeignKey('units.unit_id'),
           nullable=True),
    Column('source', Unicode, nullable=False),
    Column('target', Unicode, nullable=True))

comments_table = Table('comments', metadata,
    Column('comment_id', Integer, primary_key=True),
    Column('type', String),
    Column('unit_id', Integer, ForeignKey('units.unit_id'),
           nullable=True))


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


class Folder(RefersToDB, SearchableFolder):
    _interface = IFolder
    _table = folders_table
    annotations = None # XXX TODO

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


class FolderContainer(RefersToDB, AbstractMapping):
    _interface = IMapping

    def __init__(self, folder):
        self.folder = folder

    def add(self, key):
        folder = Folder(key)
        self.folder.subfolder_list.append(folder)
        self.db.flush()
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
        self.db.flush()
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


class Module(RefersToDB, AbstractMapping, SearchableModule):
    _interface = IModule
    _table = modules_table
    annotations = None # XXX TODO

    @property
    def template(self):
        return self[None] # XXX

    def __init__(self, key):
        self.key = key
        self.folder = None
        self.description = None

    def add(self, key):
        store = TranslationStore(key)
        self.store_list.append(store)
        self.db.flush()
        return store

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


# Translation store
# -----------------


class TranslationStore(RefersToDB):
    _interface = ITranslationStore
    _table = stores_table

    @property
    def header(self):
        return HeaderContainer(self)

    def translate(self, source, plural=0):
        s = self.db.session.query(TranslationPair).select(
            and_(trans_table.c.source == source,
                 trans_table.c.plural_idx == plural,
                 trans_table.c.parent_id == units_table.c.unit_id,
                 units_table.c.parent_id == self.store_id))
        if len(s) == 0:
            raise ValueError(source)
        assert len(s) == 1
        return s[0].target

    def find(self, substring):
        substring = substring.replace('*', '%')
        s = self.db.session.query(TranslationUnit).select(
            and_(or_(trans_table.c.source.like(substring),
                     trans_table.c.target.like(substring)),
                 trans_table.c.parent_id == units_table.c.unit_id,
                 units_table.c.parent_id == self.store_id))
        # TODO: plurals, search limit, window, etc.
        return s

# TODO: Use a result proxy, something like this:
#        q = units_table.select(trans_table.c.source.like(substring)
#                   & (trans_table.c.parent_id == units_table.c.unit_id))
#        return q.execute_using(self.db.engine).fetchall()

    @property
    def annotations(self):
        return StoreAnnotationContainer(self)

    def __init__(self, key):
        self.key = key
        self.module = None

    def __iter__(self):
        return iter(self.unit_list)

    def __len__(self):
        return len(self.unit_list)

    def __getitem__(self, idx):
        return self.unit_list[idx]

    def __getslice__(self, start, end):
        return self.unit_list[start:end]

    def makeunit(self, trans):
        return TranslationUnit(trans)

    def fill(self, units):
        for unit in list(self.unit_list):
            self.unit_list.remove(unit)
        for i, unit in enumerate(units):
            unit.idx = i
            self.unit_list.append(unit)

    def save(self):
        self.db.flush()


class TranslationUnit(RefersToDB):
    _interface = ITranslationUnit
    _table = units_table

    context = None # TODO
    annotations = None # TODO

    @property
    def comments(self):
        return CommentContainer(self)

    @property
    def annotations(self):
        return UnitAnnotationContainer(self)

    def _get_trans(self):
        return [(trans.source, trans.target)
                for trans in self.trans_list]
    def _set_trans(self, trans):
        for old_pair in list(self.trans_list):
            self.trans_list.remove(old_pair)
        for i, (source, target) in enumerate(trans):
            pair = TranslationPair(i, source, target)
            self.trans_list.append(pair)
    trans = property(_get_trans, _set_trans)

    def __init__(self, trans):
        self.trans = trans


class TranslationPair(object):
    _table = trans_table

    def __init__(self, plural_idx, source, target):
        self.plural_idx = plural_idx
        self.source = source
        self.target = target


class CommentContainer(AbstractMapping):
    """A helper for accessing comments."""

    def __init__(self, unit):
        self.unit = unit

    def add(self, type, comment):
        comment = Comment(type, comment)
        self.unit.comment_list.append(comment)

    def __getitem__(self, type):
        result = []
        for comment in self.unit.comment_list:
            if comment.type == type:
                result.append(comment.comment)
        return result

    def keys(self):
        keys = set(comment.type for comment in self.unit.comment_list)
        return list(keys)


class Comment(object):
    _table = comments_table

    def __init__(self, type, comment):
        self.type = type
        self.comment = comment


class HeaderContainer(AbstractMapping):
    """A helper for storing headers."""

    def __init__(self, store):
        self.store = store

    def add(self, key, value):
        header = Header(key, value)
        self.store.header_list.append(header)

    def __delitem__(self, key):
        for header in self.store.header_list:
            if header.key == key:
                self.store.header_list.remove(header)
                return

    def __getitem__(self, key):
        for header in self.store.header_list:
            if header.key == key:
                return header.value
        else:
            raise KeyError(key)

    def keys(self):
        return [header.key for header in self.store.header_list]


class Header(object):
    _table = headers_table

    def __init__(self, key, value):
        self.key = key
        self.value = value


class Annotation(object):

    def __init__(self, key, value):
        self.key = key
        self.value = value


class AnnotationContainer(AbstractMapping):
    # TODO: refactor similarity to HeaderContainer.
    _interface = IMapping

    annotationfactory = None # override this

    def __init__(self, parent):
        self.parent = parent

    def add(self, key, value):
        annotation = self.annotationfactory(key, value)
        self.parent.annotation_list.append(annotation)

    def __setitem__(self, key, value):
        try:
            del self[key]
        except KeyError:
            pass
        self.add(key, value)

    def __delitem__(self, key):
        for annotation in self.parent.annotation_list:
            if annotation.key == key:
                self.parent.annotation_list.remove(annotation)
        else:
            raise KeyError(key)

    def __getitem__(self, key):
        for annotation in self.parent.annotation_list:
            if annotation.key == key:
                return annotation.value
        else:
            raise KeyError(key)

    def keys(self):
        return [annotation.key for annotation in self.parent.annotation_list]


class StoreAnnotation(Annotation):
    _table = store_annotations_table
class StoreAnnotationContainer(AnnotationContainer):
    annotationfactory = StoreAnnotation


class UnitAnnotation(Annotation):
    _table = unit_annotations_table
class UnitAnnotationContainer(AnnotationContainer):
    annotationfactory = UnitAnnotation


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
        self.session.save(self.root)
        self.flush()

    def create_tables(self):
        global metadata
        metadata.create_all(engine=self.engine)

    def flush(self):
        self.session.flush()

    def refresh(self, obj):
        self.session.refresh(obj)

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
                     backref=backref("store")),
        'header_list': relation(Header, private=True),
        'annotation_list': relation(StoreAnnotation, private=True),
    })

mapper(Header, headers_table)
mapper(StoreAnnotation, store_annotations_table)

mapper(TranslationUnit, units_table,
    properties={
        'index': units_table.c.idx,
        'trans_list': relation(TranslationPair, private=True, lazy=False,
                               order_by=trans_table.c.plural_idx),
        'comment_list': relation(Comment, private=True, lazy=False),
        'annotation_list': relation(UnitAnnotation, private=True),
    })

mapper(UnitAnnotation, unit_annotations_table)

mapper(TranslationPair, trans_table)

mapper(Comment, comments_table)
