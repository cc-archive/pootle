"""Implementation of the storage API on top of the standard Pootle storage.

The standard Pootle storage is a tree of directories with .po files.

Only read-only access is provided at the moment and there is no caching.
"""

import os

from Pootle.storage.po import read_po, write_po
from Pootle.storage.abstract import AbstractMapping
from Pootle.storage.api import IDatabase, IFolder, IModule, ITranslationStore
from Pootle.storage.api import IMapping
from Pootle.storage.memory import TranslationStore as MemTranslationStore
from Pootle.storage.memory import LanguageInfoContainer \
        as MemLanguageInfoContainer


class HaveStatistics(object):
    def statistics(self):
        raise NotImplementedError('TODO')


class Database(HaveStatistics, AbstractMapping):
    _interface = IDatabase

    key = None
    folder = None

    languages = None
    modules = None
    subfolders = None

    def __init__(self, root_path):
        self.modules = {}
        self.subfolders = FolderContainer(root_path, self)
        self.languages = MemLanguageInfoContainer(self)

    def __getitem__(self, key):
        return self.subfolders[key]

    def startTransaction(self):
        pass
    def commitTransaction(self):
        pass
    def rollbackTransaction(self):
        pass


class FolderContainer(AbstractMapping):
    _interface = IMapping

    def __init__(self, root_path, db):
        self.root_path = root_path
        self.db = db

    def keys(self):
        return os.listdir(self.root_path)

    def __getitem__(self, key):
        if key in self.keys():
            path = os.path.join(self.root_path, key)
            return Folder(path, key, self.db)
        else:
            raise KeyError(key)

    def __delitem__(self, key):
        raise NotImplementedError() # TODO

    def add(self, key):
        # TODO: Register project in Pootle configuration file.
        if key in self.keys():
            raise KeyError(key)
        folder_path = os.path.join(self.root_path, key)
        os.mkdir(path)
        return self[key]


class Folder(HaveStatistics, AbstractMapping):
    _interface = IFolder

    folder = None
    modules = None
    subfolders = None
    key = None

    def __init__(self, path, key, db):
        self.modules = ModuleContainer(path, self)
        self.subfolders = {}
        self.key = key
        self.folder = db

    def __getitem__(self, key):
        return self.modules[key]


class ModuleContainer(AbstractMapping):
    _interface = IMapping

    def __init__(self, path, folder):
        self.path = path # path to folder
        self.folder = folder

    def keys(self):
        # Return modules for which there are templates or translations.
        modulenames = []
        for lang in os.listdir(self.path):
            langdir = os.path.join(self.path, lang)
            for fn in os.listdir(langdir):
                if fn.endswith('.po'):
                    modulenames.append(fn[:-len('.po')])
                elif fn.endswith('.pot'):
                    modulenames.append(fn[:-len('.pot')])
        return modulenames

    def __getitem__(self, key):
        if key in self.keys():
            return Module(self.path, key, self.folder)
        else:
            raise KeyError(key)

    def __delitem__(self, key):
        raise NotImplementedError()

    def add(self, key):
        if key in self.keys():
            raise KeyError(key)
        else:
            module = Module(self.path, key, self.folder)
            template = module.add(None)
            template.save() # Create an empty template
            return template


class Module(HaveStatistics, AbstractMapping):
    _interface = IModule

    key = None
    folder = None
    description = None
    name = None
    checker = None

    def __init__(self, path, key, folder):
        self.path = path
        self.key = key
        self.name = key
        self.folder = folder

    @property
    def template(self):
        pot_path = os.path.join(self.path, 'templates', self.key + '.pot')
        if not os.path.exists(pot_path):
            return None
        pot_text = file(pot_path).read()
        store = TranslationStore(self, None, pot_path)
        read_po(pot_text, store)
        return store

    def keys(self):
        langkeys = []
        for lang in os.listdir(self.path):
            modpath = os.path.join(self.path, lang, self.key + '.po')
            if os.path.exists(modpath):
                langkeys.append(lang)
        return langkeys

    def _langinfo(self, lang_key):
        db = self.folder.folder
        langs = db.languages
        try:
            langinfo = langs[lang_key]
        except KeyError:
            langinfo = db.languages.add(lang_key) # TODO: stop-gap measure.
        return langinfo

    def __getitem__(self, lang_key):
        if lang_key in self.keys():
            po_path = os.path.join(self.path, lang_key, self.key + '.po')
            potext = file(po_path).read()
            langinfo = self._langinfo(lang_key)
            store = TranslationStore(self, langinfo, po_path)
            read_po(potext, store)
            return store
        else:
            raise KeyError(lang_key)

    def __delitem__(self, key):
        raise NotImplementedError() # TODO

    def values(self):
        # TODO: A generator would be nicer here.
        return [self[key] for key in self.keys()]

    def items(self):
        return [(key, self[key]) for key in self.keys()]

    def add(self, lang_key):
        if lang_key is None: # template
            if self.template is not None:
                raise KeyError(None)
            lang_dir = os.path.join(self.path, 'templates')
            if not os.path.exists(lang_dir):
                os.mkdir(lang_dir)
            pot_path = os.path.join(self.path, 'templates', self.key + '.pot')
            return TranslationStore(self, None, pot_path)
        else:
            if lang_key in self.keys():
                raise KeyError(lang_key)
            lang_dir = os.path.join(self.path, lang_key)
            if not os.path.exists(lang_dir):
                os.mkdir(lang_dir)
            po_path = os.path.join(self.path, lang_key, self.key + '.po')
            return TranslationStore(self, lang_key, po_path)


class TranslationStore(MemTranslationStore):

    def __init__(self, module, lang_key, po_path):
        langinfo = None # XXX TODO: dig out of DB, register in pootle.prefs.
        MemTranslationStore.__init__(self, module, langinfo)
        self.po_path = po_path

    def save(self):
        # TODO: Locking?
        pofile = file(self.po_path, 'w')
        data = write_po(self)
        pofile.write(data)
        pofile.close()
