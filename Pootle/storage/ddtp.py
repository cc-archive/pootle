#!/usr/bin/python
"""DDTP support.

Use cases:
  1) import DDTP strings to Pootle (or merge with existing ones)
  2) export strings from Pootle to DDTP files

TODO:
- merging!
- unwrap and divide text into paragraphs for easier translation
- divide module into several modules to make .po files smaller

"""

import os
import sys
import md5

# Note: it appears that Debian's Packages is encoded in Latin-1, while
# files from DDTP are encoded in UTF-8.

def parse_template(f, charset='latin1'):
    """Parse package descriptions from a Packages file.

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
                description = ''.join(description)
                md5sum = md5.md5(description).hexdigest()
                packages.append((name, md5sum, description.decode(charset)))
                name = None
                description = None

    if description:
        description = ''.join(description)
        md5sum = md5.md5(description).hexdigest()
        packages.append((name, md5sum, description.decode(charset)))

    return packages


def parse_translation(f, charset='utf-8'):
    """Parse a DDTP translation from a file.

    Returns (lang, [(name, md5sum, description)]).

    `md5sum` is the MD5 checksum of the description in English.
    """
    charset = 'utf-8' # The DDTP files seem to be in UTF-8.
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
                description = ''.join(description)
                packages.append((name, md5sum, description.decode(charset)))
                name = None
                description = None
    if description:
        description = ''.join(description)
        packages.append((name, md5sum, description.decode(charset)))
    return lang, packages


class DDTPModule(object):
    """A wrapper for a folder that stores DDTP translations.

    Internally the strings are distributed among several modules in order
    to reduce the size of translation stores.

    This class has methods to read/write data into either DDTP translation
    format or the Pootle database storage.
    """

    parsed_template = None # set in import_template

    def __init__(self, folder):
        self.folder = folder

    # --- Import ---

    def import_template(self, template):
        """Import DDTP description translations into Pootle."""
        template_store = DDTPStore(self, None)

        self.parsed_template = parse_template(template)
        for (name, md5sum, description) in self.parsed_template:
            template_store.add_package(name, md5sum, description, None)
        template_store.save()

    def import_translations(self, translations):
        """Import DDTP description translations into Pootle.

        Overwrites old translations.
        TODO: do proper merging.

        import_template() has to be invoked before calling this method.

        template is a file-like object containing the descriptions (Packages).
        translations is a list of file-like objects which contain the
        translations (e.g., Translation-de).
        """
        for translation in translations:
            units = []
            lang_key, parsed_translation = parse_translation(translation)
            self.import_translation(lang_key, parsed_translation)
            break # XXX Process only one language; makes testing faster.

    def import_translation(self, lang_key, parsed_translation):
        """Import a single translation into Pootle."""
        # Build a lookup dict.
        lookup = {}
        for (name, md5sum, description) in parsed_translation:
            lookup[name, md5sum] = description

        translation_store = DDTPStore(self, lang_key)
        for (name, md5sum, description) in self.parsed_template:
            trans = [(description, )]
            translation_store.add_package(name, md5sum, description,
                                         lookup.get((name, md5sum)))
            # TODO: mark fuzzy if lookup fails
        translation_store.save()

    # --- Export ---

    def export_to_ddtp(self, translations_dir):
        """Export data from Pootle to DDTP.

        `translations_dir` is the directory where to put Translation-?? files.
        If non-existent, it is created.
        """
        if not os.path.exists(translations_dir):
            os.mkdir(translations_dir)

        for lang_key in self.list_languages():
            ddtpstore = DDTPStore(self, lang_key)
            ddtpstore.load()

            fn = 'Translation-%s' % lang_key
            path = os.path.join(translations_dir, fn)
            self.export_store(ddtpstore, file(path, 'w'))

    def list_languages(self):
        """List all available languages."""
        modules = self.folder.modules
        modname = modules.keys()[0] # Pick first package.
        module = modules[modname]
        return module.keys()

    ddtp_entry = """Package: %(name)s
Description-md5: %(md5)s
Description-%(lang)s: %(description)s
"""

    def export_store(self, ddtpstore, stream, charset='utf-8'):
        """Export a DDTPStore to DDTP format."""
        for package_info in ddtpstore.list_packages():
            name, md5sum, description, translation = package_info
            if translation:
                args = dict(name=str(name),
                            md5=str(md5sum),
                            lang=str(ddtpstore.key),
                            description=translation.encode(charset))
                stream.write(self.ddtp_entry % args)


class DDTPStore(object):
    """A DDTP translation store wrapper."""

    def __init__(self, ddtpmodule, key):
        self.ddtpmodule = ddtpmodule
        self.key = key
        self._modules = {}

    def moduleName(self, package_name):
        """Pick the name of the module where the package will end up."""
        if not package_name.startswith('lib'):
            # Use the first letter of the package name.
            return package_name[0]
        else:
            # A lot of packages are libraries and therefore have the prefix
            # 'lib'.  In this case we will include the first letter of the
            # library name.
            return package_name[:4]

    def add_package(self, name, md5sum, description, translation):
        """Register a package in the store."""
        info = (name, md5sum, description, translation)
        modname = self.moduleName(name)
        self._modules.setdefault(modname, []).append(info)

    def list_packages(self):
        """List all packages in the store.

        Returns a list of tuples (name, md5sum, description, translation),
        sorted by name.
        """
        packages = []
        for modname in sorted(self._modules.keys()):
            packages.extend(self._modules[modname])
        return packages

    def load(self):
        """Load store state from Pootle database."""
        self._modules.clear()
        modules = self.ddtpmodule.folder.modules
        modnames = sorted(modules.keys())
        for modname in modnames:
            self._modules[modname] = packages = []
            module = modules[modname]
            store = module[self.key]
            for unit in store:
                description, translation = unit.trans[0]
                name, md5sum = unit.automatic_comments
                packages.append((name, md5sum, description, translation))

    def save(self):
        """Save current state of the store to Pootle database."""
        for modname, packages in self._modules.items():
            try:
                module = self.ddtpmodule.folder.modules[modname]
            except KeyError:
                module = self.ddtpmodule.folder.modules.add(modname)

            if self.key is None:
                store = module.template
                if store is None:
                    store = module.add(None)
            else:
                try:
                    store = module[self.key]
                except KeyError:
                    store = module.add(self.key)

            units = []
            for (name, md5sum, description, translation) in packages:
                trans = [(description, translation)]
                unit = store.makeunit(trans)
                unit.automatic_comments = [name, md5sum]
                units.append(unit)
            store.fill(units)
            store.save()




# --- executable part ---

usage = """Usage:

ddtp.py import <path/to/Packages> <path/to/translations> <pootle_db_dir>
ddtp.py export <pootle_db_dir> <path/to/translations>
"""


sys.path.append('../../')
from Pootle.storage.standard import Database as Database


def gather_translation_files(translations_dir):
    translation_fns = os.listdir(translations_dir)
    translation_files = []
    for translation_fn in translation_fns:
        if '.' in translation_fn: # the file is probably an archive, skip it
            continue
        if not translation_fn.startswith('Translation-'):
            continue
        translation_file = file(os.path.join(translations_dir, translation_fn))
        translation_files.append(translation_file)
    return translation_files

def do_import(template_path, translations_dir, pootle_db_dir):
    """Import DDTP templates and translations into Pootle.

    `template_path` is a path to the Packages index.
    `translations_dir` is the path of the directory where Translation-?? files
    reside.
    `pootle_db_dir` is the path to the Pootle .po store.

    XXX: perform merging!
    """

    db = Database(pootle_db_dir)
    try:
        folder = db.subfolders['ddtp']
    except KeyError: # Need to create folder.
        folder = db.subfolders.add('ddtp')

    module = DDTPModule(folder)
    template = file(template_path)
    module.import_template(template)
    translation_files = gather_translation_files(translations_dir)
    module.import_translations(translation_files)


def do_export(pootle_db_dir, translations_dir):
    """Export DDTP translations from Pootle.

    `pootle_db_dir` is the path to the Pootle .po store.
    Currently the project 'ddtp' is picked from there.
    `translations_dir` is the path to the directory where to
    put Translation-?? files.
    """
    db = Database(pootle_db_dir)
    try:
        folder = db.subfolders['ddtp']
    except KeyError: # Need to create folder.
        folder = db.subfolders.add('ddtp')

    module = DDTPModule(folder)
    module.export_to_ddtp(translations_dir)


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
