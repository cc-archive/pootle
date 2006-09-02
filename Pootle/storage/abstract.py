"""Abstract classes for use as base classes."""


class AbstractMapping(object):
    """An abstract mapping.

    You still need to provide keys(), __getitem__(), __setitem__() and
    __delitem__().
    """

    def __len__(self):
        return len(self.keys())

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def items(self):
        return [(key, self[key]) for key in self.keys()]

    def values(self):
        return [self[key] for key in self.keys()]

    def itervalues(self):
        for key in self.keys():
            yield self[key]


class SearchableFolder(object):
    """A mixin that provides naive brute-force search for folders."""

    def find(self, *args, **kwargs):
        units = []
        for module in self.modules.values():
            units.extend(module.find(*args, **kwargs))
        for folder in self.subfolders.values():
            units.extend(folder.find(*args, **kwargs))
        return units

    def find_containers(self, substring):
        fs, ms = [], [] # folders, modules
        for module_name in self.modules.keys():
            if substring in module_name:
                ms.append(self[module_name])
        for folder in self.subfolders.values():
            f, m = folder.find_containers(substring)
            fs.extend(f)
            ms.extend(m)
        return fs, ms


class SearchableModule(object):

    def find(self, *args, **kwargs):
        units = []
        for store in self.values():
            units.extend(store.find(*args, **kwargs))
        return units


class SearchableTranslationStore(object):
    """Naive implementation of search in a translation store."""

    def find(self, substring, search_source=True, search_target=True,
             limit=None, offset=None, exact=False):
        # This is pretty slow.
        assert not exact and '*' not in substring, 'not implemented yet'
        units = []
        for unit in self:
            for source, target in unit.trans:
                if ((search_source and substring in source) or
                    (search_target and substring in target)):
                    units.append(unit)
        end = None
        if limit is not None:
            if offset is not None:
                end = limit + offset
            else:
                end = limit
        return units[offset:end]
