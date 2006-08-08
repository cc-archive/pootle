#!/usr/bin/python
"""DDTP support."""

import os
import sys
import md5


def parse_template(f):
    """Parse package descriptions from a file.

    Returns a list [(name, md5sum, description)].

    `md5sum` is the MD5 checksum of the description.
    """
    packages = []

    name = None
    description = None
    for line in f:
        if line.startswith('Package: '):
            name = line.split(' ', 1)[1].strip()
        elif line.startswith('Description: '):
            description = [line.split(' ', 1)[1]]
        elif description:
            if line.startswith(' '):
                description.append(line) # Another line of the description.
            else:
                md5sum = md5.md5(''.join(description)).hexdigest()
                packages.append((name, md5sum, ''.join(description)))
                name = None
                description = None

    if description:
        md5sum = md5.md5(''.join(description)).hexdigest()
        packages.append((name, md5sum, ''.join(description)))

    return packages


def parse_translation(f):
    """Parse a DDTP translation from a file.

    Returns (lang, [(name, md5sum, description)]).

    `md5sum` is the MD5 checksum of the description in English.
    """
    packages = []

    name = None
    description = None
    for line in f:
        if line.startswith('Package: '):
            name = line.split(' ', 1)[1].strip()
        elif line.startswith('Description-md5: '):
            md5sum = line.split(' ', 1)[1].strip()
        elif line.startswith('Description-'):
            lang = line.split(':')[0].split('-')[1]
            description = [line.split(' ', 1)[1]]
        elif description:
            if line.startswith(' '):
                description.append(line) # Another line of the description.
            else:
                # XXX Decode to unicode before importing?
                packages.append((name, md5sum, ''.join(description)))
                name = None
                description = None
    if description:
        packages.append((name, md5sum, ''.join(description)))
    return lang, packages


def import_descriptions(module, template, translations):
    """Imports DDTP description translations into IModule.

    Overwrites old translations.
    TODO: do proper merging.

    template is a file-like object containing the descriptions (Packages).
    translations is a list of file-like objects which contain the
    translations (e.g., Translation-de).
    """
    template_store = module.makestore(None)

    units = []
    parsed_template = parse_template(template)
    for (name, md5sum, description) in parsed_template:
        trans = [(description, None)]
        unit = template_store.makeunit(trans)
        unit.automatic_comments = [name, md5sum]
        units.append(unit)
    template_store.fill(units)
    module.template = template_store

    for translation in translations:
        units = []
        lang, parsed_translation = parse_translation(translation)

        # Build a lookup dict.
        lookup = {}
        for (name, md5sum, description) in parsed_translation:
            lookup[name, md5sum] = description

        # Populate module.
        translation_store = module.add(lang)
        for (name, md5sum, description) in parsed_template:
            trans = [(description, lookup.get((name, md5sum)))]
            unit = translation_store.makeunit(trans)
            unit.automatic_comments = [name, md5sum]
            units.append(unit)
        translation_store.fill(units)


ddtp_entry = """Package: %(name)s
Description-md5: %(md5)s
Description-%(lang)s: %(description)s
"""

def export_translation(store, stream):
    for unit in store:
        name, md5sum = unit.automatic_comments
        translation = unit.trans[0][1]
        if translation:
            args = dict(name=name, md5=md5sum, lang=store.key,
                        description=translation.encode('utf-8'))
            stream.write(ddtp_entry % args)


def export_translations(module, translations_dir):
    for store in module.values():
        filename = os.path.join(translations_dir, 'Translation-%s' % store.key)
        export_translation(store, file(filename, 'w'))


# --- executable part ---

usage = """Usage:

ddtp.py import <path/to/Packages> <path/to/translations> <project_dir>
ddtp.py export <project_dir> <path/to/translations>
"""


sys.path.append('../../')
from Pootle.storage.memory import Database
from Pootle.storage.po import export_module_to_pootle, import_module_from_pootle


def do_import(template_path, translations_dir, project_dir):
    """Import DDTP templates and translations into Pootle.

    `template_path` is a path to the Packages index.
    `translations_dir` is the path of the directory where Translation-?? files
    reside.
    `project_dir` is the path of the corresponding Pootle project.

    XXX: perform merging!
    """
    template = file(template_path)
    translation_fns = os.listdir(translations_dir)
    translation_files = []
    for translation_fn in translation_fns:
        if '.' in translation_fn: # the file is probably an archive, skip it
            continue
        if not translation_fn.startswith('Translation-'):
            continue
        translation_file = file(os.path.join(translations_dir, translation_fn))
        translation_files.append(translation_file)

    db = Database()
    module = db.modules.add('ddtp')
    import_descriptions(module, template, translation_files)
    export_module_to_pootle(module, project_dir)


def do_export(project_dir, translations_dir):
    """Export DDTP translations from Pootle.

    `project_dir` is the path of the corresponding Pootle project.
    `translations_dir` is the path of the directory where to
    put Translation-?? files.
    """
    db = Database()
    module = db.modules.add('ddtp')
    import_module_from_pootle(project_dir, module)
    export_translations(module, translations_dir)


def main(argv=[]):
    if len(argv) < 2:
        print usage
        sys.exit(1)
    cmd = argv[1]
    if cmd == 'import':
        do_import(argv[2], argv[3], argv[4])
    elif cmd == 'export':
        do_export(argv[2], argv[3])
    else:
        print usage
        sys.exit(1)


if __name__ == '__main__':
    main(sys.argv)
