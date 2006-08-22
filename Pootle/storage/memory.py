"""A backend that stores all the data directly in objects.

If needed, the database can be trivially serialized by use of pickle.
"""

from Pootle.storage.api import IStatistics, IDatabase, ITranslationUnit
from Pootle.storage.api import ILanguageInfo, IModule, IMapping, IFolder
from Pootle.storage.api import ITranslationStore, IHaveStatistics
from Pootle.storage.api import IHeader
from Pootle.storage.abstract import AbstractMapping, SearchableModule
from Pootle.storage.abstract import SearchableFolder, SearchableTranslationStore


class MappingMixin(AbstractMapping):
    _interface = IMapping

    def __init__(self):
        self._items = {}

    def keys(self):
        return self._items.keys()

    def values(self):
        return self._items.values()

    def items(self):
        return self._items.items()

    def __getitem__(self, key):
        return self._items[key]

    def __delitem__(self, key):
        del self._items[key]

    def __len__(self):
        return len(self._items)

    def add(self, name):
        raise NotImplementedError("override this")


class AccumStatsMixin(object):
    _interface = IHaveStatistics

    def statistics(self):
        stats = Statistics()
        for item in self.values():
            itemstats = item.statistics()
            stats.accum(itemstats)
        return stats


class ModuleContainer(MappingMixin):

    def __init__(self, folder):
        MappingMixin.__init__(self)
        self.folder = folder

    def add(self, key):
        if key in self._items:
            raise KeyError(key)
        module = self._items[key] = Module(key, self.folder)
        return module


class FolderContainer(MappingMixin):

    def __init__(self, folder):
        MappingMixin.__init__(self)
        self.folder = folder

    def add(self, key):
        # TODO: check that a module with this key does not exist
        newfolder = self._items[key] = Folder(key, self.folder)
        return newfolder


class Folder(AccumStatsMixin, SearchableFolder):
    _interface = IFolder

    db = None
    key = None
    folder = None
    annotations = None

    modules = None
    subfolders = None

    def __init__(self, key, folder, db=None):
        self.key = key
        self.folder = folder
        if db is not None:
            self.db = db
        else:
            self.db = folder.db
        self.modules = ModuleContainer(self)
        self.subfolders = FolderContainer(self)
        self.annotations = {}

    def __repr__(self):
        return '<Folder %s>' % self.key

    def __getitem__(self, key):
        try:
            return self.subfolders[key]
        except KeyError:
            return self.modules[key]

    def __len__(self):
        return len(self.modules) + len(self.subfolders)

    def values(self):
        # This is for internal use in AccumStatsMixin.
        return self.modules.values() + self.subfolders.values()


class LanguageInfoContainer(MappingMixin):

    def __init__(self, db):
        self.db = db
        MappingMixin.__init__(self)

    def add(self, key):
        lang = self._items[key] = LanguageInfo(self.db)
        if '_' in key:
            lang.code, lang.country = key.split('_')
        else:
            lang.code = key
        assert lang.key == key
        return lang


class Database(object):
    _interface = IDatabase

    root = None
    languages = None

    def __init__(self):
        self.root = Folder(None, None, db=self)
        self.languages = LanguageInfoContainer(self)

    def startTransaction(self):
        pass

    def commitTransaction(self):
        pass

    def rollbackTransaction(self):
        raise NotImplementedError("rollback not supported")

    def flush(self):
        pass # not needed

    def refresh(self, obj):
        raise NotImplementedError('not supported')


class LanguageInfo(object):
    _interface = ILanguageInfo
    db = None

    code = None
    country = None

    @property
    def key(self):
        if self.country is not None:
            return '%s_%s' % (self.code, self.country.upper())
        else:
            return self.code

    name = None
    name_eng = None
    specialchars = None
    nplurals = None
    pluralequation = None

    def __init__(self, db):
        self.db = db


class Module(MappingMixin, AccumStatsMixin, SearchableModule):
    _interface = IModule

    db = None
    key = None
    folder = None
    annotations = None

    name = None
    description = None
    checker = None
    template = None

    def __init__(self, key, folder):
        MappingMixin.__init__(self)
        self.db = folder.db
        self.key = key
        self.folder = folder
        self.name = key # until something else is set
        self.annotations = {}

    def __repr__(self):
        return '<Module %s>' % self.key

    def add(self, lang_key, copy_template=False):
        # TODO: handle copy_template.
        # TODO: refactor
        if lang_key is not None:
            if lang_key in self._items:
                raise KeyError(lang_key)
            langs = self.db.languages
            try:
                langinfo = langs[lang_key]
            except KeyError:
                langinfo = self.db.languages.add(lang_key) # TODO: stop-gap measure.
            store = TranslationStore(self, langinfo)
            self._items[lang_key] = store
        else:
            if self.template is not None:
                raise KeyError(lang_key)
            store = TranslationStore(self, None)
            self.template = store # TODO: document this
        return store


class Header(MappingMixin):
    _interface = IHeader

    store = None

    def __init__(self, store):
        self.store = store
        MappingMixin.__init__(self)
        self._order = []

    def keys(self):
        return self._order[:]

    def values(self):
        return [self[k] for k in self._order]

    def items(self):
        return [(k, self[k]) for k in self._order]

    def __delitem__(self, key):
        MappingMixin.__delitem__(self, key)
        del self._order[key]

    def add(self, key, value):
        if key in self._order:
            raise KeyError(key)
        self._order.append(key)
        self._items[key] = value

    __setitem__ = add


class TranslationStore(SearchableTranslationStore):
    _interface = ITranslationStore

    module = None
    header = None
    langinfo = None
    annotations = None

    @property
    def key(self):
        return self.langinfo.key

    def __init__(self, module, langinfo):
        self.module = module
        self.langinfo = langinfo
        self._units = []
        self.header = Header(self)
        self.annotations = {}

    def __iter__(self):
        return iter(self._units)

    def __len__(self):
        return len(self._units)

    def __getitem__(self, number):
        return self._units[number]

    def __getslice__(self, start, end):
        return self._units[start:end]

    def fill(self, units):
        self._units = []
        for i, unit in enumerate(units):
            unit.index = i
            self._units.append(unit)

    def save(self):
        pass # We're in memory already.

    def makeunit(self, trans):
        """See TranslationUnit.__init__."""
        return TranslationUnit(self, trans)

    def translate(self, source, plural=0):
        for unit in self._units:
            if len(unit.trans) > plural and unit.trans[plural][0] == source:
                return unit.trans[plural][1]
        else:
            raise ValueError('no translation found for %r' % source)

    def statistics(self):
        stats = Statistics()
        stats.total_strings = len(self)
        for unit in self:
            if 'fuzzy' in unit.comments.get('type', []):
                stats.fuzzy_strings += 1
            else:
                for source, target in unit.trans:
                    if not target:
                        break
                else:
                    stats.translated_strings += 1
        return stats


class CommentContainer(MappingMixin):
    _interface = IMapping

    def add(self, comment_type, comment):
        lst = self._items.setdefault(comment_type, [])
        lst.append(comment)


class TranslationUnit(object):
    _interface = ITranslationUnit

    store = None
    index = None
    annotations = None
    context = None

    comments = None

    trans = None

    def __init__(self, store, trans):
        """Construct a TranslationUnit.

        trans should be a list of tuples (source, target).
        """
        self.store = store
        self.trans = trans
        # TODO: assert len(trans) == language.nplurals?
        self.annotations = {}
        self.comments = CommentContainer()


class Statistics(object):
    _interface = IStatistics

    total_strings = None
    translated_strings = None
    fuzzy_strings = None

    def __init__(self, total_strings=0, translated_strings=0, fuzzy_strings=0):
        self.total_strings = total_strings
        self.translated_strings = translated_strings
        self.fuzzy_strings = fuzzy_strings

    def accum(self, otherstats):
        self.total_strings += otherstats.total_strings
        self.translated_strings += otherstats.translated_strings
        self.fuzzy_strings += otherstats.fuzzy_strings
