"""Abstract classes (interfaces) that define the Pootle backend API.

These classes only describe the available operations.  New backends should
implement operations described here.

Fields marked as optional can have the value None.

You can use the function validateModule to check that a set of backend classes
implements the interfaces described here.


Here is a rough sketch of the class containment hierarchy:

  IDatabase
    IFolder
      ...
        IModule (maps to a .pot file)
          ITranslationStore (one for each language)
            ITranslationUnit (maps to a msgid)


Object lifecycle semantics
==========================

All content objects (folders, modules, translation stores, etc.) are
to be simultaneously created and added to a container.  Afterwards their
name or reference to parent must not be changed. The only exception is
TranslationUnits which are constructed and added in separate steps.

This policy allows the backend to commit changes immediately and avoid floating
unserialized objects.

"""

# === Helper objects ===

class Interface(object):
    """An interface."""

# Fields
class Field(Interface):
    """An attribute that stores a particular type of data."""

class String(Field): pass
class Unicode(Field): pass
class Username(Unicode): pass
class Id(Unicode): pass
class Integer(Field): pass
class Boolean(Field): pass
class Date(Field): pass
class Class(Field): pass


# === API interfaces ===

class IHaveStatistics(Interface):
    """An object that can provide translation statistics."""

    def statistics(self):
        """Return statistics for this object.

        Returns an IStatistics object.
        """


class IStatistics(Interface):
    """Statistics.

    Several plurals are counted as a single string.

    Fuzzy strings are not counted as translated.
    """

    total_strings = Integer
    translated_strings = Integer
    fuzzy_strings = Integer
    # TODO: untranslated, but suggested? word counts? other?

    def accum(self, otherstats):
        """Add up statistics from another IStatistics object."""


class IMapping(Interface):

    def keys(self):
        """Return list of object keys."""
        return [String]

    def values(self):
        """Return list of object values."""
        return [object]

    def itervalues(self):
        """Return iterator over values."""
        return iter

    def items(self):
        """Return list of tuples (key, value)."""
        return [(String, object)]

    def __getitem__(self, key):
        """Get object by key."""
        return object

    def __delitem__(self, key):
        """Delete key from container."""

    def __len__(self):
        """Return length of store."""
        return Integer

    def add(self, key):
        """Create a new object, add it to this container and return it."""
        return object


class IFolder(IHaveStatistics):
    """A folder is a collection of modules and possibly other folders."""

    key = String
    folder = None # =IFolder -- containing folder (not the subcontainer)

    modules = IMapping # name -> IModule
    subfolders = IMapping # name -> IFolder

    def __getitem__(self, key):
        """Return a module or a subfolder.

        A subfolder is preferred to a module if they have the same name.

        This is a convenience method; it is usually better to use
        folder.modules[] or subfolder.modules[] directly.
        """

    def __len__(self):
        return Integer


class IDatabase(IFolder):
    """A database.

    This acts as the root of the content object hierarchy.

    Its constructor may accept arbitrary arguments for configuration.
    TODO: unified way to open a database (a config parser object)?
    """

    languages = IMapping # 'la_CO' -> ILanguageInfo

    def startTransaction(self):
        """Start a transaction.

        Does nothing if transactions are not supported.
        May enable exclusive file locks in case of a file-based backend.
        """

    def commitTransaction(self):
        """Commit a transaction.

        Does nothing if transactions are not supported.
        May disable exclusive file locks in case of a file-based backend.
        """

    def rollbackTransaction(self):
        """Commit a transaction.

        Does nothing if transactions are not supported.
        """


class ILanguageInfo(Interface):
    """Basic information about a language.

    One ILanguageInfo object exists for each language, stored in
    IDatabase.languages.  Copies of translation stores for the same
    language should reference the same language info instance.
    """

    db = IDatabase # XXX Why not ILanguageContainer?

    # TODO: inheritance? e.g., pt_BR from pt.  Could be tricky.

    code = String # ISO639 language code (lowercase)
    country = String # optional - ISO3166 two-letter country code (uppercase)
    key = String # Should be a property.  E.g., 'en', 'pt_BR', etc.
    name = Unicode # complete language name (native)
    name_eng = Unicode # complete language name in English; optional
    specialchars = [Unicode] # list of special chars
    nplurals = Integer
    pluralequation = String # optional


class IModule(IHaveStatistics, IMapping):
    """An object corresponding to a project.

    This loosely corresponds to a .pot file and a set of its translations.

    Maps 'la_CO' identifiers to TranslationStores.

    A module contains a 'template' translation store (no translations) and
    a set of translation stores with translated data.

    Note that the different translations can differ structurally from the
    normal template.  The differences can be resolved using merging as an
    external process.
    """

    key = Id # module id
    folder = IFolder # containing folder
    name = Unicode # module name
    description = Unicode # project description (unwrapped)
    checker = [String] # A list of string identifiers for checkers
    template = Interface # ITranslationStore without the actual translations
    # TODO: template == store[None] ?

    def add(self, key, copy_template=False):
        """Create a new empty TranslationStore bound to this module.

        `lang_key` is a language identifier, e.g., 'pt_BR' or 'lt'.
        If `lang_key` is None, the resulting template will be put into
        the `template` attribute.
        If `copy_template` is True, the template will be copied on the
        new translation store.
        """
        return ITranslationStore


class IHeader(IMapping):
    """Information about a translation store (maps to a .po header).

    Behaves like an ordered dictionary: keys() should return an ordered list.
    New entries are added at the end.  Insertion is not provided (if needed,
    the header can be recreated).
    """

    store = None # Parent ITranslationStore


class ITranslationStore(IHaveStatistics):
    """A collection of translation units

    This loosely corresponds to a .po file.

    Note that the internal container of translation units is not exposed
    directly so that the implementation can accurately track all changes.

    For efficiency reasons modifications are not recorded immediately.
    Call save() explicitly when you are done modifying the data.
    TODO: is this really needed?
    """

    module = IModule
    header = IHeader # maps to a .po header
    langinfo = ILanguageInfo
    key = String # e.g., 'pt_BR'

    def __iter__(self):
        """Return an iterable of translation units."""
        return iter(ITranslationUnit)

    def __len__(self):
        return Integer

    def __getitem__(self, number):
        """Get translation by index (starting from 0)."""
        return IMessage

    def __getslice__(self, start, end):
        """Return a half-open range (by number) of translations.

        This allows slice-notation: store[0:5] would get the first 5
        units.
        """

    def fill(self, units):
        """Clear this store and import list of units from given iterable."""

    def save(self):
        """Save the current state of this store to persistent storage."""
        # TODO: is this really needed if we have 'fill'?

    def makeunit(self, trans):
        """Construct a new translation unit.

        Only put units constructed by this method inside this store, or
        set their store attribute.

        trans is a list of tuples (source, target).  `source` and `target`
        should be unicode values.  Target may be None.
        """

    def translate(self, source, plural=0):
        """Translate the given source message.

        If a plural is requested, its index must be provided.

        Raises ValueError if source is not found.
        """


class ISuggestion(Interface):
    """A suggestion for a particular message.

    The intention of this class is to store an unapproved string, possibly
    submitted by an irregular or even unregistered translator.  The user
    interface should offer a convenient way of "upgrading" suggestions to
    translations.
    """

    unit = None # =ITranslationUnit
    date = Date # submission date
    author = Username # author's user name -- optional


class ITranslationUnit(Interface):
    """A translatable string.

    Plurals and metadata are also stored here.
    """

    store = ITranslationStore
    suggestions = [ISuggestion]
    context = Unicode # context information

    # Comments; taken straight off translate.storage.po.pounit
    # Maybe these should be put into a subobject?
    other_comments = [Unicode]     #  # this is another comment
    automatic_comments = [Unicode] #  #. comment extracted from the source code
    source_comments = [Unicode]    #  #: sourcefile.xxx:35
    type_comments = [Unicode]      #  #, fuzzy
    visible_comments = [Unicode]   #  #_ note to translator  (this is nonsense)
    obsolete_messages = [Unicode]  #  #~ msgid ""
    msgid_comments = [Unicode]     #  _: within msgid
    # TODO: type comments are special. Abstract them.

    # Use the XLIFF model here: plural sources are stored together with targets
    # The list of tuples is ordered.  If a plural is not translated, the target
    # in the tuple should be None.  When copying a translation unit from a
    # template, this list may have to be enlarged if the target language
    # has more than 2 plurals.
    # For singular, just use a single tuple in the list.
    trans = [(Unicode,  # plural msgid (source)
              Unicode)] # plural translation (target)

    # TODO: it would be nice to have a "dirty" attribute


# === Merging ===

class IMerger(object):
    """An object that can merge translation files."""

    def merge(self, translation, template):
        """Update translation from template.

        Modifies the translation object in place.

        translation and template are translation stores.

        TODO: It would be nicer to return a new TranslationStore.
        """


# === Validation helpers ===

# TODO: I'm reinventing the wheel here, poorly.  I would like to grab a
# real interface package such as zope.interface or pyprotocols, but that
# would be an additional dependency.

class ImplementationError(Exception):
    pass


blacklist = ['__dict__', '__doc__', '__module__', '__weakref__']

def iface_attrs(iface):
    attrs = iface.__dict__.items()
    for base in iface.__bases__:
        attrs.extend(iface_attrs(base))
    for attr in blacklist:
        if attr in attrs:
            attrs.remove(attr)
    return attrs


def validateClass(cls, iface):
    """Validate a given class against an interface."""
    for attrname, attr in iface_attrs(iface):

        # Check for existence of the attribute
        try:
            real_attr = getattr(cls, attrname)
        except AttributeError:
            raise ImplementationError('%r does not have %r' % (cls, attrname))

        if isinstance(attr, type) and issubclass(attr, Interface): # attribute
            pass
        elif callable(attr): # method
            if not callable(real_attr):
                raise ImplementationError('%r of %r is not callable'
                                          % (attrname, cls))


def validateModule(module, complete=False):
    """Check classes in a module against interfaces.

    The classes to be checked should have the atttribute _interface
    pointing to the implemented interface.
    """
    ifaces = set()
    for name, cls in module.__dict__.items():
        if isinstance(cls, type):
            iface = getattr(cls, '_interface', None)
            if iface is not None:
                validateClass(cls, iface)
                ifaces.add(iface)

    if complete:
        pass # TODO: check if all interfaces were implemented at least once?
