"""A .po file importer and exporter.

Uses translate.storage.po classes to parse/serialize .po translations.
"""

import os
from translate.storage.po import pofile


comment_types = dict(other_comments='#',
                     automatic_comments='#.',
                     source_comments='#:',
                     type_comments='#,',
                     visible_comments='#_',
                     obsolete_messages='#~',
                     msgid_comments='')

comment_attrs = ['other_comments', 'automatic_comments', 'source_comments',
                 'type_comments', 'visible_comments', 'obsolete_messages',
                 'msgid_comments']


def read_po(potext, store):
    """Fill TranslationStore store with data in potext.

    `potext` can be a string or a file-like object.

    Imports the header separately.  Deals with plurals.
    """
    po = pofile(potext)
    store.header = po.parseheader() # uses ordereddict from jToolkit
    units = []
    for oldunit in po.units:
        if oldunit.isheader():
            continue
        try:
            trans = [(unicode(oldunit.source), unicode(oldunit.target))]
        except UnicodeDecodeError: # XXX
            trans = [(u'b0rk', u'')]
            print oldunit.msgid
        if oldunit.hasplural():
            plural_msgid = unicode(oldunit.source.strings[1])
            for s in oldunit.target.strings[1:]:
                trans.append((plural_msgid, unicode(s)))
        unit = store.makeunit(trans)
        for attr in comment_attrs:
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
    po.updateheader(add=True, **store.header)
    for unit in store:
        msgid = [trans[0] for trans in unit.trans]
        pounit = po.UnitClass(msgid)
        if len(unit.trans) == 1:
            pounit.target = unit.trans[0][1]
        else:
            pounit.target = [trans[1] for trans in unit.trans]
        for attr in comment_attrs:
            values = getattr(unit, attr, [])
            for value in values:
                comment = '%s %s\n' % (comment_types[attr], value)
                getattr(pounit, attr.replace('_', '')).append(comment)
        po.units.append(pounit)

    return po.getoutput()


# --- Interfacing with Pootle ---

# TODO: write a proper transparent Pootle-storage-compatible backend.

def export_module_to_pootle(module, project_dir):
    """Export translations from an IModule to Pootle as a Pootle project.

    The required directories are created automatically, but the project
    itself needs to be set up and `project_dir` must already exist.

    Beware: existing files will be overwritten.  Files on the filesystem
    but not in the given module are not touched. TODO: clean them up?
    """
    template_dir = os.path.join(project_dir, 'templates')
    try:
        os.mkdir(template_dir)
    except OSError, e:
        if e.errno != 17: # file already exists
            raise

    template_file = os.path.join(template_dir, '%s.pot' % module.key)
    template_data = write_po(module.template)
    file(template_file, 'w').write(template_data)

    for store in module.values():
        translation_dir = os.path.join(project_dir, store.langinfo.key)
        try:
            os.mkdir(translation_dir)
        except OSError, e:
            if e.errno != 17: # file already exists
                raise
        translation_file = os.path.join(translation_dir, '%s.po' % module.key)
        translation_data = write_po(store)
        file(translation_file, 'w').write(translation_data)


def import_module_from_pootle(project_dir, module):
    """Import an IModule from Pootle.

    Imports the template and any translations.
    """
    template_file = os.path.join(project_dir, 'templates',
                                 '%s.pot' % module.key)
    module.add(None)
    read_po(file(template_file).read(), module.template)

    for language in os.listdir(project_dir):
        if language == 'templates':
            continue
        print language # XXX
        store = module.add(language)
        translation_file = os.path.join(project_dir, language,
                                        '%s.po' % module.key)
        read_po(file(translation_file), store)
