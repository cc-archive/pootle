"""A backend that stores all the data directly in objects.

If needed, the database can be trivially serialized by use of pickle.
"""

from Pootle.storage.api import IStatistics, IDatabase, ITranslationUnit
from Pootle.storage.api import ILanguageInfo, IModule, IMapping, IFolder
from Pootle.storage.api import ITranslationStore, ISuggestion, IHaveStatistics


class MappingMixin(object):
    _interface = IMapping
    # TODO: just subclass dict?

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


class Folder(AccumStatsMixin):
    _interface = IFolder

    key = None
    folder = None

    modules = None
    subfolders = None

    def __init__(self, key, folder):
        self.key = key
        self.folder = folder
        self.modules = ModuleContainer(self)
        self.subfolders = FolderContainer(self)

    def __repr__(self):
        return '<Folder %s>' % self.key

    def __getitem__(self, key):
        try:
            return 'module', self.modules[key]
        except KeyError:
            return 'folder', self.subfolders[key]

    def __len__(self):
        return len(self.modules) + len(self.subfolders)

    def values(self):
        # This is for internal use in AccumStatsMixin.
        return self.modules.values() + self.subfolders.values()


class Database(Folder):
    _interface = IDatabase

    def __init__(self):
        Folder.__init__(self, None, None)


class LanguageInfo(object):
    _interface = ILanguageInfo

    code = None
    country = None
    name = None
    name_eng = None
    specialchars = None
    nplurals = None
    pluralequation = None

    def __init__(self, code, country=None, name=None, name_eng=None,
                 specialchars=None, nplurals=None, pluralequation=None):
        self.code = code
        self.country = country
        self.name = name
        self.name_eng = name_eng
        self.specialchars = specialchars
        self.nplurals = nplurals
        self.pluralequation = pluralequation


class Module(MappingMixin, AccumStatsMixin):
    _interface = IModule

    key = None
    folder = None

    name = None
    description = None
    checker = None
    template = None

    def __init__(self, key, folder):
        MappingMixin.__init__(self)
        self.key = key
        self.folder = folder
        self.name = key # until something else is set

    def __repr__(self):
        return '<Module %s>' % self.key

    def add(self, language, country):
        raise NotImplementedError('XXX TODO')


class TranslationStore(object):
    _interface = ITranslationStore

    module = None
    langinfo = None
    key = None # TODO property

    def __init__(self, name, module, langinfo):
        self.name = name
        self.module = module
        self.langinfo = langinfo
        self._units = []

    def __iter__(self):
        return iter(self._units)

    def __len__(self):
        return len(self._units)

    def __getitem__(self, number):
        return self._units[number]

    def __getslice__(self, start, end):
        return self._units[start:end]

    def fill(self, units):
        self._units = [] # TODO: unlink the previous units?
        for unit in units:
            self._units.append(unit) # TODO: link new units?

    def save(self):
        raise NotImplementedError()

    def makeunit(self, trans):
        """See TranslationUnit.__init__."""
        return TranslationUnit(self, trans)

    def statistics(self):
        stats = Statistics()
        stats.total_strings = len(self)
        for unit in self:
            if unit.fuzzy:
                stats.fuzzy_strings += 1
            else:
                for source, target in unit.trans:
                    if not target:
                        break
                else:
                    stats.translated_strings += 1
        return stats


class Suggestion(object):

    _interface = ISuggestion

    unit = None
    date = None
    author = None

    def __init__(self, unit, date, author):
        self.unit = unit
        self.date = date
        self.author = author


class TranslationUnit(object):
    _interface = ITranslationUnit

    collection = None
    suggestions = None
    context = None

    translator_comments = None
    automatic_comments = None
    reference = None

    datatype = None
    fuzzy = False

    trans = None

    def __init__(self, collection, trans):
        """Construct a TranslationUnit.

        trans should be a list of tuples (source, target).
        """
        self.collection = collection
        self.trans = trans
        # TODO: assert len(trans) == language.nplurals?


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
