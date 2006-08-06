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
            name = line.split(' ', 1)[1]
            name = name[:-1] # XXX chomp trailing newline
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
            name = line.split(' ', 1)[1]
            name = name[:-1] # XXX chomp trailing newline - could be \r\n
        elif line.startswith('Description-md5: '):
            md5sum = line.split(' ', 1)[1]
            md5sum = md5sum[:-1] # XXX chomp trailing newline - could be \r\n
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
            units.append(unit)
        translation_store.fill(units)


# --- executable part ---

usage = """Usage:

ddtp.py import <path/to/Packages> <path/to/translations> <project_dir>
"""


sys.path.append('../../')
from Pootle.storage.memory import Database
from Pootle.storage.po import write_po


def do_import(template_path, translations_dir, project_dir):
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
    export_descriptions_to_pootle(module, project_dir)


def export_descriptions_to_pootle(module, project_dir):
    template_dir = os.path.join(project_dir, 'templates')
    try:
        os.mkdir(template_dir)
    except OSError, e:
        if e.errno != 17: # file already exists
            raise

    template_file = os.path.join(template_dir, 'ddtp.pot')
    template_data = write_po(module.template)
    file(template_file, 'w').write(template_data)

    for store in module.values():
        translation_dir = os.path.join(project_dir, store.langinfo.key)
        try:
            os.mkdir(translation_dir)
        except OSError, e:
            if e.errno != 17: # file already exists
                raise
        translation_file = os.path.join(translation_dir, 'ddtp.po')
        translation_data = write_po(store)
        file(translation_file, 'w').write(translation_data)


def main(argv=[]):
    if len(argv) < 2:
        print usage
        sys.exit(1)
    cmd = argv[1]
    if cmd == 'import':
        do_import(argv[2], argv[3], argv[4])
    else:
        print usage
        sys.exit(1)


if __name__ == '__main__':
    main(sys.argv)
