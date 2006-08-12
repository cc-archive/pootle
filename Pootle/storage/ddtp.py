#!/usr/bin/python
"""DDTP support.

Use cases:
  1) import DDTP strings to Pootle
  2) import new templates from Packages
  3) export strings from Pootle to DDTP files

TODO:
- Differentiate merging templates and merging translations.
- Merge new templates with old translations.

"""

import os
import sys
import md5
import textwrap


class DDTPPackage(object):

    def __init__(self, name, md5sum, paras=None):
        """Create a DDTP package.

        You may pass in `paras`, which should be a list of tuples:
        [(description_paragraph, translated_paragraph)].
        `translated_paragraph` may be None.
        """
        self.name = name
        self.md5sum = md5sum
        self.paras = paras

    def import_description(self, description, translation):
        """Import RFC822-style description and translation."""
        description_paras = self._split(description)
        if translation:
            translation_paras = self._split(translation)
            assert len(description_paras) == len(translation_paras), \
                   translation_paras
        else:
            translation_paras = [None] * len(description_paras)
        self.paras = zip(description_paras, translation_paras)

    def istranslated(self):
        return bool(self.paras[0][1])

    ddtp_entry_template = textwrap.dedent("""\
    Package: %(name)s
    Description-md5: %(md5)s
    Description-%(lang)s: %(short)s
    %(description)s
    """)

# Description format documentation can be found here:
# http://www.debian.org/doc/debian-policy/ch-controlfields.html#s-f-Description

    def export(self, lang_key, charset='utf-8'):
        """Export to RFC822-style description."""
        assert self.istranslated()
        short = self.paras[0][1]
        description = self._export_description(
            [trans for desc, trans in self.paras[1:]])
        args = dict(name=str(self.name),
                    md5=str(self.md5sum),
                    lang=str(lang_key),
                    short=str(short),
                    description=description.encode(charset))
        return self.ddtp_entry_template % args

    def _export_description(self, paras):
        rows = []
        wrapper = textwrap.TextWrapper(width=76, initial_indent=' ',
                                       subsequent_indent=' ',
                                       replace_whitespace=False)
        wrapped_paras = []
        for para in paras:
            wrapped_lines = []
            for line in para.splitlines():
                if not line.startswith(' '): # Wrapping is allowed.
                    line = wrapper.fill(line)
                else:
                    # Normally the leading space is added by the wrapper.
                    line = ' ' + line
                wrapped_lines.append(line)
            wrapped_paras.append('\n'.join(wrapped_lines))
        return '\n .\n'.join(wrapped_paras)

    def _split(self, description):
        lines = description.splitlines()
        short_desc = lines[0]

        paras = [] # list of paragraphs
        para = '' # current paragraph
        for line in lines[1:] + [' .']:
            assert line[0] == ' '
            line = line[1:] # Remove the leading space.
            if line == '.':
                paras.append(para)
                para = ''
            elif line[0].isspace():
                para += '\n' + line
            else:
                if para: # Connect two lines by space.
                    para += ' ' + line
                else:
                    para = line
        return [short_desc] + paras

    def make_units(self, makeunit):
        """Make a list of translation units for a package description.

        `makeunit` is a callable that creates a translation
        (typically SomeTranslationStore.makeunit).
        """
        units = []
        for i, para in enumerate(self.paras):
            unit = makeunit([para])
            comment = '%s (%d/%d)  MD5: %s' % (self.name, i+1,
                                                 len(self.paras), self.md5sum)
            unit.automatic_comments = [comment]
            units.append(unit)
        return units

    @staticmethod
    def _parseComment(comment):
        name, mid, note, md5sum = comment.split()
        i, total = mid[1:-1].split('/')
        return name, int(i), int(total), md5sum

    @staticmethod
    def parse_units(units):
        """Parse an iterable of translation units into DDTPPackage objects.

        Note that you can just pass in a TranslationStore.

        Returns a list of DDTPPackages.
        """
        packages = []
        paras = []
        for unit in units:
            description, translation = unit.trans[0]
            [comment] = unit.automatic_comments
            name, i, total, md5sum = DDTPPackage._parseComment(comment)
            paras.append(unit.trans[0])

            # The following 'if' is purely for checking validity:
            # check that the sequence of paragraphs has consistent metadata.
            if i == 1: # first paragraph
                p_name = name
                p_i = 1
                p_total = total
                p_md5sum = md5sum
            else:
                p_i += 1
                assert p_name == name, name
                assert p_i == i, i
                assert p_total == total, total
                assert p_md5sum == md5sum, md5sum

            if i == total: # Last paragraph, create a package.
                package = DDTPPackage(name, md5sum, paras)
                packages.append(package)
                paras = []
        return packages


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

        self.parsed_template = self.parse_template(template)
        # TODO: This deserves to be inside DDTPStore.
        for (name, md5sum, description) in self.parsed_template:
            package = DDTPPackage(name, md5sum)
            package.import_description(description, None)
            template_store.add_package(package)
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
            lang_key, parsed_translation = self.parse_translation(translation)
            translation_store = DDTPStore(self, lang_key)
            translation_store.import_store(self.parsed_template,
                                           parsed_translation)
            translation_store.save()
            break # XXX Process only one language; makes testing faster.

    # Note: it appears that Debian's Packages is encoded in Latin-1, while
    # files from DDTP are encoded in UTF-8.

    def parse_template(self, f, charset='latin1'):
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


    def parse_translation(self, f, charset='utf-8'):
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
                    description = ''.join(description)
                    packages.append((name, md5sum, description.decode(charset)))
                    name = None
                    description = None
        if description:
            description = ''.join(description)
            packages.append((name, md5sum, description.decode(charset)))
        return lang, packages

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
            ddtpstore.export_store(file(path, 'w'))

    def list_languages(self):
        """List all available languages."""
        modules = self.folder.modules
        modname = modules.keys()[0] # Pick first package.
        module = modules[modname]
        return module.keys()


class DDTPStore(object):
    """A DDTP translation store wrapper.

    Stores DDTP translations.  Provides methods to write the translations
    to Pootle storage or to DDTP files.
    """

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

    def add_package(self, package):
        """Register a package in the store."""
        modname = self.moduleName(package.name)
        self._modules.setdefault(modname, []).append(package)

    def list_packages(self):
        """List all packages in the store.

        Returns a list of DDTPPackages sorted by name.
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
            module = modules[modname]
            store = module[self.key]
            for package in DDTPPackage.parse_units(store):
                self.add_package(package)

    def save(self):
        """Save current state of the store to Pootle database."""
        for modname, packages in self._modules.items():
            try:
                module = self.ddtpmodule.folder.modules[modname]
            except KeyError:
                module = self.ddtpmodule.folder.modules.add(modname)

            if self.key is None:
                store = module.template
            else:
                store = module.get(self.key)
            if store is None:
                store = module.add(self.key)

            units = []
            for package in packages:
                units.extend(package.make_units(store.makeunit))
            store.fill(units)
            store.save()

    def export_store(self, stream):
        """Export a DDTPStore to DDTP format."""
        for package in self.list_packages():
            stream.write(package.export(self.key))

    def import_store(self, parsed_template, parsed_translation):
        """Import a DDTP-format translation into Pootle.

        Overwrites current contents of the store.
        TODO: merging

        parsed_translation is a list of tuples (name, md5sum, description).
        """
        # Build a lookup dict.
        lookup = {}
        for (name, md5sum, description) in parsed_translation:
            lookup[name, md5sum] = description

        for (name, md5sum, description) in parsed_template:
            package = DDTPPackage(name, md5sum)
            translation = lookup.get((name, md5sum))
            package.import_description(description, translation)
            self.add_package(package)
            # TODO: mark fuzzy by name if lookup fails.


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
