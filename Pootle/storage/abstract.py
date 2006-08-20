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

    def find(self, substring):
        # TODO: This is very slow.
        units = []
        for module in self.values():
            units.extend(module.find(substring))
        for folder in self.subfolders:
            units.extend(folder.find(substring))
        return units

    def find_containers(self, substring):
        fs, ms = [], [] # folders, modules
        for module_name in self.keys():
            if substring in module_name:
                ms.append(self[module_name])
        for folder in self.subfolders:
            f, m = folder.find_containers(substring)
            fs.extend(f)
            ms.extend(m)
        return fs, ms


class SearchableModule(object):

    def find(self, substring):
        # TODO: This is very slow.
        units = []
        for store in self.values():
            units.extend(store.find(substring))
        return units


class SearchableTranslationStore(object):

    def find(self, substring):
        # TODO: This is very slow.
        units = []
        for unit in self:
            for source, target in unit.trans:
                if substring in source or substring in target:
                    units.append(unit)
        return units
