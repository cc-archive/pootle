"""A .po file importer and exporter.

Uses translate.storage.po classes to parse/serialize .po translations.
"""

from translate.storage.po import pofile

def read_po(potext, store):
    """Fill TranslationStore store with data in potext."""
    po = pofile(potext)
    units = []
    for oldunit in po.units:
        # TODO: comments, etc.
        trans = [(str(oldunit.source), str(oldunit.target))]
        if oldunit.hasplural():
            plural_msgid = str(oldunit.source.strings[1])
            for s in oldunit.target.strings[1:]:
                trans.append((plural_msgid, str(s)))
        unit = store.makeunit(trans)
        units.append(unit)
    store.fill(units)


def write_po(module):
    pass # TODO
