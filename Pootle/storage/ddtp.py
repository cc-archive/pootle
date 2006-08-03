"""DDTP support."""

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
            name = name[:-1] # XXX chomp trailing newline
        elif line.startswith('Description-md5: '):
            md5sum = line.split(' ', 1)[1]
            md5sum = md5sum[:-1] # XXX chomp trailing newline
        elif line.startswith('Description-'):
            lang = line.split(':')[0].split('-')[1]
            description = [line.split(' ', 1)[1]]
        elif description:
            if line.startswith(' '):
                description.append(line) # Another line of the description.
            else:
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

    template is a file object containing the descriptions (Packages).
    translations is a list of file objects which contain the
    translations (e.g., Translation-de)."""
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
        translation_store = module.makestore(lang)
        for (name, md5sum, description) in parsed_template:
            trans = [(description, lookup.get((name, md5sum)))]
            unit = translation_store.makeunit(trans)
            units.append(unit)
        translation_store.fill(units)
        module._items[lang] = translation_store # XXX Breaks abstraction!
