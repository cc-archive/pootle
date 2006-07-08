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
        IModule (maps to a .po file)
          ITranslationStore (one for each language)
            ITranslationUnit

"""

# === Helper objects ===

class Interface(object): pass

# Fields
class String(Interface): pass
class Unicode(Interface): pass
class Username(Unicode): pass
class Id(Unicode): pass
class Integer(Interface): pass
class Boolean(Interface): pass
class Date(Interface): pass
class Class(Interface): pass


# === API interfaces ===

class IHaveStatistics(Interface):
    """An object that can provide translation statistics."""

    def statistics(self):
        """Return statistics for this object."""
        return IStatistics


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

    # TODO: specify traversal precedence
    key = String
    folder = None # =IFolder -- containing folder (not the subcontainer)

    modules = IMapping # name -> IModule
    subfolders = IMapping # name -> IFolder

    def __getitem__(self, key):
        """Return a module or a subfolder.

        Returns a tuple ('module', module_obj) or a tuple ('folder', folder).
        """

    def __len__(self):
        return Integer


class IDatabase(IFolder):
    """A database."""

    # TODO: start/end transaction? (if supported)


class ILanguageInfo(Interface):
    """Basic information about a language."""

    # TODO: Specify if this object could/should be shared between projects.

    # TODO: use simple ln/ln_LN as primary key instead of tuple?
    code = String # ISO639 language code
    country = String # optional - ISO3166 two-letter country code
    name = Unicode # complete language name (native)
    name_eng = Unicode # complete language name in English; optional TODO needed?
    specialchars = [Unicode] # list of special chars
    nplurals = Integer
    pluralequation = String # optional


class IModule(IHaveStatistics, IMapping):
    """An object corresponding to a project.

    This loosely corresponds to a .pot file and a set of its translations.

    Maps (language, country) to TranslationStore.

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
    # TODO: Have a link to the project's ViewVC page so that we can produce
    #       direct hyperlinks to unit context in the source code.


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
    langinfo = ILanguageInfo
    key = (String, String) # (code, country): should be a property that gets
                           # the data from langinfo; country may be None.

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
        update their store attribute.

        trans is a list of tuples (source, target).
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

    # Comments: optional; can be multiline, but should be whitespace-stripped
    translator_comments = Unicode
    automatic_comments = Unicode
    reference = Unicode # TODO Should we be smarter here?

    datatype = String # optional -- c-format, no-c-format, java-format, etc.
    fuzzy = Boolean

    # Use the XLIFF model here: plural sources are stored together with targets
    # The list of tuples is ordered.  If a plural is not translated, the target
    # in the tuple should be None.  When copying a translation unit from a
    # template, this list may have to be enlarged if the target language
    # has more than 2 plurals.
    # For singular, just use a single tuple in the list.
    trans = [(Unicode,  # plural msgid (source)
              Unicode)] # plural translation (target)

    # TODO: it would be nice to have a "dirty" attribute


# === Validation helpers ===

# TODO: I'm reinventing the wheel here, poorly.  I would like to grab a
# real interface package such as zope.interface, but that would be an
# additional dependency.

class ImplementationError(Exception):
    pass


def iface_attrs(iface):
    attrs = iface.__dict__.items()
    for base in iface.__bases__:
        attrs.extend(iface_attrs(base))
    return attrs


def validateClass(cls, iface):
    """Validate a given class against an interface."""
    for attrname, attr in iface_attrs(iface):
        if attrname.startswith('__'):
            continue # ignore internal attributes

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
            # TODO check signature of callable?
#        else:
#            raise AssertionError("shouldn't happen")


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
