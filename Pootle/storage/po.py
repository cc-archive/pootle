"""A .po file importer and exporter.

Uses translate.storage.po classes to parse/serialize .po translations.
"""

from translate.storage.po import pofile


comment_types = dict(other_comments='#',
                     automatic_comments='#.',
                     source_comments='#:',
                     type_comments='#,',
                     visible_comments='#_',
                     obsolete_messages='#~',
                     msgid_comments='')


def read_po(potext, store):
    """Fill TranslationStore store with data in potext.

    Imports the header separately.  Deals with plurals.
    """
    po = pofile(potext)
    store.header = po.parseheader() # uses ordereddict from jToolkit
    units = []
    for oldunit in po.units:
        if oldunit.isheader():
            continue
        trans = [(str(oldunit.source), str(oldunit.target))]
        if oldunit.hasplural():
            plural_msgid = str(oldunit.source.strings[1])
            for s in oldunit.target.strings[1:]:
                trans.append((plural_msgid, str(s)))
        unit = store.makeunit(trans)
        for attr in ['other_comments', 'automatic_comments', 'source_comments',
                     'type_comments', 'visible_comments', 'obsolete_messages',
                     'msgid_comments']:
            values = getattr(oldunit, attr.replace('_', ''), [])
            for value in values:
                start = len(comment_types[attr])
                value = value[start+1:-1] # chomp leading #? and trailing \n
                getattr(unit, attr).append(value)
        units.append(unit)
    store.fill(units)


def write_po(store):
    """Serialize translation store to .po format."""
    po = pofile()
    for unit in store:
        msgid = [trans[0] for trans in unit.trans]
        pounit = po.UnitClass(msgid)
        pounit.target = [trans[1] for trans in unit.trans]
        for attr in ['other_comments', 'automatic_comments', 'source_comments',
                     'type_comments', 'visible_comments', 'obsolete_messages',
                     'msgid_comments']:
            values = getattr(unit, attr, [])
            for value in values:
                comment = '%s %s\n' % (comment_types[attr], value)
                getattr(pounit, attr.replace('_', '')).append(comment)
        po.units.append(pounit)

    return po.getoutput()
