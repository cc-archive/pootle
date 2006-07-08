"""A .po file importer and exporter.

Uses translate.storage.po classes to parse/serialize .po translations.
"""

from translate.storage.po import pofile

def read_po(potext, store):
    """Fill TranslationStore store with data in potext."""
    po = pofile(potext)
    units = []
    for oldunit in po.units:
        # TODO: plurals, comments, etc.
        trans = [(str(oldunit.source), str(oldunit.target))]
        unit = store.makeunit(trans)
        units.append(unit)
    store.fill(units)


def write_po(module):
    pass # TODO
