"""A .po file importer and exporter.

Uses translate.storage.po classes to parse/serialize .po translations.
"""

import os
from translate.storage.po import pofile


comment_types = dict(other='#',
                     automatic='#.',
                     source='#:',
                     type='#,',
                     visible='#_',
                     obsolete='#~',
                     msgid='')


def read_po(potext, store):
    """Fill TranslationStore store with data in potext.

    `potext` can be a string or a file-like object.

    Imports the header separately.  Deals with plurals.
    """
    po = pofile(potext)
    for key in store.header.keys():
        del store.header[key] # clear the header
    for name, value in po.parseheader().items():
        store.header.add(name, value)
    units = []
    for oldunit in po.units:
        if oldunit.isheader():
            continue
        trans = [(unicode(oldunit.source), unicode(oldunit.target))]
        if oldunit.hasplural():
            plural_msgid = unicode(oldunit.source.strings[1])
            for s in oldunit.target.strings[1:]:
                trans.append((plural_msgid, unicode(s)))
        unit = store.makeunit(trans)
        for attr in comment_types.keys():
            values = getattr(oldunit, attr + 'comments', [])
            for value in values:
                if value.startswith('# Annotation: '):
                    # XXX The split is not reliable -- " = " could occur
                    # inside the annotation.
                    key, val = value[len('# Annotation: '):].split(' = ')
                    key = eval(key) # XXX Handle escapes -- security hole!
                    val = eval(val) # XXX Handle escapes -- evil!
                    unit.annotations[key] = val
                else:
                    start = len(comment_types[attr])
                    value = value[start+1:-1] # chomp leading #? and trailing \n
                    value = unicode(value) # TODO: specify charset?
                    unit.comments.add(attr, value)
        units.append(unit)
    store.fill(units)


def write_po(store):
    """Serialize translation store to .po format."""
    po = pofile()
    po.updateheader(add=True, **dict(store.header.items()))
    for unit in store:
        msgid = [trans[0] for trans in unit.trans]
        pounit = po.UnitClass(msgid)
        if len(unit.trans) == 1:
            pounit.target = unit.trans[0][1]
        else:
            pounit.target = [trans[1] for trans in unit.trans]
        for attr in comment_types.keys():
            values = unit.comments.get(attr, [])
            for value in values:
                comment = '%s %s\n' % (comment_types[attr], value)
                getattr(pounit, attr + 'comments').append(comment)
            annotation_comments = pounit.othercomments
        for key, value in unit.annotations.items():
            annotation_comments.append('# Annotation: %r = %r\n'
                                       % (key, value))
        po.units.append(pounit)

    return po.getoutput()
