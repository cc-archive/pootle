"""Abstract classes for use as base classes."""

class AbstractMapping(object):

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
