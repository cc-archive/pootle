"""Implementation of the storage API on top of the standard Pootle storage.

The standard Pootle storage is a tree of directories with .po files.

Only read-only access is provided at the moment and there is no caching.
"""

import os
from Pootle.storage.memory import TranslationStore
from Pootle.storage.po import read_po
from Pootle.storage.api import IDatabase, IFolder, IModule, ITranslationStore


class HaveStatistics(object):
    def statistics(self):
        raise NotImplementedError('TODO')


class Database(HaveStatistics):
    _interface = IDatabase

    key = None
    folder = None

    languages = None
    modules = None
    subfolders = None

    def __init__(self, root_path):
        self.subfolders = FolderContainer(root_path)

    def startTransaction(self):
        pass
    def commitTransaction(self):
        pass
    def rollbackTransaction(self):
        pass


class FolderContainer(object):

    def __init__(self, root_path):
        self.root_path = root_path

    def keys(self):
        return os.listdir(self.root_path)

    def __getitem__(self, key):
        if key in self.keys():
            path = os.path.join(self.root_path, key)
            return Folder(path, key)
        else:
            raise KeyError(key)


class Folder(HaveStatistics):
    _interface = IFolder

    folder = None
    modules = None
    subfolders = None
    key = None

    def __init__(self, path, key, db):
        self.modules = ModuleContainer(path)
        self.key = key
        self.folder = db


class ModuleContainer(object):

    def __init__(self, path):
        self.path = path

    def keys(self):
        modulenames = []
        for lang in os.listdir(self.path):
            langdir = os.path.join(self.path, lang)
            for fn in os.listdir(langdir):
                if fn.endswith('.po'):
                    modulenames.append(fn[:-len('.po')])
        return modulenames

    def __getitem__(self, key):
        if key in self.keys():
            return Module(self.path, key, self)
        else:
            raise KeyError(key)


class Module(HaveStatistics):
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
        pot_path = os.path.join(self.path, 'templates', self.key + '.po')
        pot_text = file(pot_path).read()
        store = TranslationStore(self.key, None, None)
        read_po(potext, store)
        return store

    def keys(self):
        langkeys = []
        for lang in os.listdir(self.path):
            modpath = os.path.join(self.path, lang, self.key + '.po')
            if os.path.exists(modpath):
                if '_' in lang:
                    langcode, countrycode = lang.split('_')
                else:
                    langcode, countrycode = lang, None
                langkeys.append((langcode, countrycode))
        return langkeys

    def _langdir(self, lang, country):
        if country:
            return '%s_%s' % (lang, country)
        else:
            return lang

    def __getitem__(self, (lang, country)):
        if (lang, country) in self.keys():
            langdir = self._langdir(lang, country)
            po_path = os.path.join(self.path, langdir, self.key + '.po')
            potext = file(po_path).read()
            store = TranslationStore(self.key, None, None)
            read_po(potext, store)
            return store
        else:
            raise KeyError((lang, country))

    def values(self):
        # TODO: A generator would be nicer here.
        return [self[key] for key in self.keys()]

    def items(self):
        return [(key, self[key]) for key in self.keys()]

    def add(self):
        raise NotImplementedError('TODO')

    def makestore(self):
        raise NotImplementedError('TODO')

    def clonestore(self):
        raise NotImplementedError('TODO')
