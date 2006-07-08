"""Implementation of the storage API on top of the standard Pootle storage.

The standard Pootle storage is a tree of directories with .po files.

Only read-only access is provided at the moment and there is no caching.
"""

import os
from Pootle.storage.memory import TranslationStore
from Pootle.storage.po import read_po


class Database(object):

    def __init__(self, root_path):
        self.root_path = root_path

    def keys(self):
        return os.listdir(self.root_path)

    def __getitem__(self, key):
        if key in self.keys():
            path = os.path.join(self.root_path, key)
            return Folder(path)
        else:
            raise KeyError(key)


class Folder(object):

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
            return Module(self.path, key)
        else:
            raise KeyError(key)


class Module(object):

    def __init__(self, path, key):
        self.path = path
        self.key = key

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
