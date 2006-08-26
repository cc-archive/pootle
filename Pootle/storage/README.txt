===================
Translation storage
===================

This package provides an API for storage of software translations.  This file
introduces the capabilities provided by the API and provides some usage
examples.

.. contents::

Getting started
===============

To get started, you need to instantiate a *database*, by invoking
``open_database(uri)``.  The argument ``uri`` identifies the type of backend
to be used.  There are several choices:

  ``mem://``
    simple transient memory storage *(no transaction support)*

  ``pootle:///path/to/storage/dir``
    on-disk storage compatible with Pootle *(no transaction support)*

  ``sqlite://``
    SQLite storage (transient memory storage)

  ``sqlite:////absolute/path/to/database.txt``
    SQLite storage (file, absolute path)

  ``sqlite:///relative/path/to/database.txt``
    SQLite storage (file, relative path)

  ``postgres://scott:tiger@localhost:5432/mydatabase``
    A PostgreSQL database.

  ``mysql://localhost/db``
    A MySQL database.

For the purposes of this example we will use a transient SQLite database.

    >>> from Pootle.storage import open_database
    >>> db = open_database('sqlite://')
    >>> db
    <Pootle.storage.rdb.Database object at ...>


Data organization
=================


Folders
-------

For convenience, translations can be grouped in *folders*.  The database
contains a reference to the *root folder*:

    >>> db.root
    <Pootle.storage.rdb.Folder object at ...>

A folder can contain other folders (the ``subfolders`` attribute).  The
``subfolders`` object acts much like standard dictionaries, but instead
of ``__setitem__()`` you should use ``add(key)``, which creates the
folder, attaches it to the parent folder and returns the new object.  This
way all Folder objects are always attached to a hierarchy.

Let's add a subfolder:

    >>> debian_folder = db.root.subfolders.add(u'debian')
    >>> db.root.subfolders.keys()
    [u'debian']

Subfolder objects can be retrieved using ``__getitem__()`` or ``get``:

    >>> db.root.subfolders['debian'] is debian_folder
    True
    >>> db.root.subfolders.get('debian') is debian_folder
    True
    >>> db.root.subfolders.get(u'bedouin', 'nonexistent')
    'nonexistent'

For convenience, you can retrieve subfolders directly from the folder:

    >>> db.root['debian'] is debian_folder
    True

We can add subfolders into a folder:

    >>> demo_subfolder = debian_folder.subfolders.add('demo')


Modules
-------

*Modules* define groups of translation strings.  They loosely correspond to a
gettext ``.pot`` file together with all its translations.  Modules are
manipulated pretty much the same way as subfolders:

    >>> hello_module = demo_subfolder.modules.add('hello')

    >>> demo_subfolder.modules['hello'] is hello_module
    True

For convenience you can also query the folder directly:

    >>> demo_subfolder['hello'] is hello_module
    True
    >>> db.root['debian']['demo']['hello'] is hello_module
    True


Translation stores
------------------

*Translation stores* correspond to a single gettext ``.pot`` template or a
translation of this template into a particular language.  Modules act as
containers for translation stores.

A translation store's key is the standard ISO639 code of the translation
language, e.g. ``de``, ``lt``, ``fr``.  If necessary, a country's ISO3166
can be appended like this: ``de_DE``, ``pt_BR``, etc.

    >>> store = hello_module.add('lt')
    >>> store
    <Pootle.storage.rdb.TranslationStore object at ...>

Translation units
~~~~~~~~~~~~~~~~~

Translation stores contain translation units. A *translation unit* is a single
unit to be translated.  It maps loosely to a single msgid/msgstr pair in
gettext files.  Comments and metadata are also stored on this object.

Translation units are lightweight and are treated slightly differently from
other contained objects.  They are to be instantiated using a store's
``makeunit()`` method.  The method takes a single parameter, a list of tuples
``(source, translation)`` (translation may be None if the string is not
translated).  Each tuple corresponds to a plural form, so if there are no
special plurals, there will be just one tuple.

    >>> unit1 = store.makeunit([(u'User', u'Naudotojas')])

The translations are stored in the attribute ``trans``:

    >>> unit1.trans
    [(u'User', u'Naudotojas')]

Now an example with some plurals:

    >>> unit2 = store.makeunit([(u'%d user', u'%d naudotojas'),
    ...                         (u'%d users', u'%d naudotojai'),
    ...                         (u'%d users', u'%d naudotoj\u0173')])

To add comments, use the ``comments`` attribute.  Specify the comment
type (`automatic`, `source`, `type`, ...) to ``add()``.  On lookup
a list of comments will be returned.

    >>> unit2.comments.add('source', u'source.c:123')
    >>> unit2.comments['source']
    [u'source.c:123']

After you create some translation units, they can be inserted into the
store all at once by using ``fill()``:

    >>> store.fill([unit1, unit2])

``fill()`` will clear the store prior to adding new translation units.

You can now retrieve translation units by index:

    >>> len(store)
    2
    >>> store[1].trans
    [(u'%d user', u'%d naudotojas'),
     (u'%d users', u'%d naudotojai'),
     (u'%d users', u'%d naudotoj\u0173')]

After performing changes to a database, do not forget to invoke ``save()`` to
write the changes to permanent storage:

    >>> store.save()

Translation
~~~~~~~~~~~

If you know the msgid exactly, you can retrieve the translation using
``translate()``:

    >>> store.translate(u'%d user')
    u'%d naudotojas'

If the translation is not known, you will get a ValueError:

    >>> store.translate(u'what is this?')
    Traceback (most recent call last):
        ...
    ValueError: what is this?

To retrieve plurals, use the keyword argument ``plural`` to indicate the
index of the plural you want:

    >>> store.translate(u'%d users', plural=1)
    u'%d naudotojai'
    >>> store.translate(u'%d users', plural=2)
    u'%d naudotoj\u0173'
    >>> store.translate(u'%d users', plural=42)
    Traceback (most recent call last):
        ...
    ValueError: %d users


Header
~~~~~~

Some basic metadata about a translation store can be stored in its header,
which is again a simple container object:

    >>> store.header
    <Pootle.storage.rdb.HeaderContainer object at ...>
    >>> store.header.add('Project-Id-Version', "Test")
    >>> store.header.add('PO-Revision-Date', "2006-08-20 02:03+0300")
    >>> store.header.keys()
    ['Project-Id-Version', 'PO-Revision-Date']

The standard use case is to put gettext PO headers here.

Searching
~~~~~~~~~

Translation stores can be efficiently searched.   Use the asterisk as
a wildcard.  Here's an example:

    >>> result = store.find('Naudot*')
    >>> result
    [<Pootle.storage.rdb.TranslationUnit object at ...>]
    >>> result == [unit1]
    True


Language information
--------------------

The database also contains an object that stores information about languages:

    >>> db.languages
    <Pootle.storage.memory.LanguageInfoContainer object at ...>
    >>> pt_info = db.languages.add('pt_BR')

The language description objects should contain information such as language
code, name, special characters, a plural form equation, etc. (see
``Pootle.storage.api.ILanguageInfo``)

    >>> pt_info
    <Pootle.storage.memory.LanguageInfo object at ...>
    >>> pt_info.code
    'pt'
    >>> pt_info.country
    'BR'
    >>> pt_info.name = 'Portuguese (Brazil)'

Note that this container is stored in memory, not persisted in the database,
because this is essentially static data.  Information about most languages
should be included in the distribution in the future.


Usage notes
===========


Persistence
-----------

Relational backends do not serialize every change immediately, so you will need
to *flush* your changes after making them.  Flushing is implicitly performed
when adding new modules, folders or translation stores, and when you invoke
``TranslationStore.save()``.  In other cases, e.g., when you change a value
of an attribute, you will need to invoke ``db.flush()`` manually:

    >>> hello_module.decription = u'Hello'
    >>> db.flush()

Note that you do not always need to pass around a reference to the database
object, because it is stored in most objects.

    >>> db is hello_module.db is demo_subfolder.db is store.db
    True


Transactions
------------

SQL-based backends provide support for *transactions*, which means that
several related changes can be committed atomically.  A transaction is
started using ``db.startTransaction()``:

    >>> db.startTransaction()
    >>> debian_folder.key
    u'debian'

Let's change the module's key, and flush the change:

    >>> debian_folder.key = u'doobie'
    >>> db.flush()

Now, let's roll back the change.

    >>> db.rollbackTransaction()

Note that after rolling back a transaction, objects already in memory
will *not* be reverted to their previous state.  You need to explicitly call
``db.refresh()`` on them:

    >>> debian_folder.key
    u'doobie'
    >>> db.refresh(debian_folder)
    >>> debian_folder.key
    u'debian'

In most cases you will want to use a try/finally clause to ensure atomic
commits.


Gettext support
===============

The primary data format PO/POT files (gettext).  Functions for importing &
exporting gettext files are provided in ``Pootle.storage.po``:

    >>> from Pootle.storage.po import read_po, write_po

To import a PO file, provide ``read_po()`` with PO source and an existing
translation store:

    >>> potext = r"""# Some translation
    ... msgid ""
    ... msgstr ""
    ... "Project-Id-Version: labas\n"
    ...
    ... #: ../hello.c:5
    ... msgid "Hello"
    ... msgstr "Labas"
    ... """

    >>> read_po(potext, store)
    >>> store[0].trans
    [(u'Hello', u'Labas')]
    >>> store[0].comments['source']
    [u'../hello.c:5']

It is trivial to import .po files directly from the web or from version
control systems with appropriate libraries.

To export a PO file, call write_po with the store as an argument.  It will
return the serialized .po as a string (with the header as necessary).

    >>> print write_po(store) # doctest: +REPORT_UDIFF
    msgid ""
    msgstr ""
    "Project-Id-Version: labas\n"
    "Report-Msgid-Bugs-To: \n"
    "POT-Creation-Date: ...\n"
    "PO-Revision-Date: ...\n"
    "Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
    "Language-Team: LANGUAGE <LL@li.org>\n"
    "MIME-Version: 1.0\n"
    "Content-Type: text/plain; charset=CHARSET\n"
    "Content-Transfer-Encoding: ENCODING\n"
    "Plural-Forms: nplurals=INTEGER; plural=EXPRESSION;\n"
    "X-Generator: Translate Toolkit ...\n"
    <BLANKLINE>
    #: ../hello.c:5
    msgid "Hello"
    msgstr "Labas"
    <BLANKLINE>


Extensions
==========

Annotations
-----------

The basic data storage model is quite limited.  However, it can be extended
by utilizing *annotations*.  Annotations are simple mappings of keys to string
values.  Most objects (folders, modules, translation stores, translation units)
are annotatable.

Limiting ourselves to a simple model plus annotations allows easy serialization
to more ordinary formats such as gettext (where the annotations can be encoded
into comments in order to preserve data during import/export), while any
extra information available in richer data formats (e.g., XLIFF) can be
preserved.

Note that annotations store plain 8-bit strings, but they can be used to
store arbitrary Python objects by use of ``pickle``.

Let's look at a translation store's annotations:

    >>> store.annotations
    <Pootle.storage.rdb.StoreAnnotationContainer object at ...>
    >>> print store.annotations.get('version')
    None
    >>> store.annotations['version'] = '0.1'
    >>> store.annotations['version']
    '0.1'


Adapters
--------

Annotations might look handy at first glance to store random metadata.  For
more complex use cases you may want an adapter that exposes a simple interface
and encapsulates all low-level access to annotations.  Here is a very simple
example:

    >>> class VersionedAdapter(object):
    ...     def __init__(self, obj):
    ...         self.obj = store
    ...     def _get_version(self):
    ...         return self.obj.annotations.get('version')
    ...     def _set_version(self, value):
    ...         self.obj.annotations['version'] = value
    ...     version = property(_get_version, _set_version)

Sample usage:

    >>> versioned = VersionedAdapter(store)
    >>> versioned.version = '0.2'
    >>> versioned.version
    '0.2'


Proxies
-------

In some cases you may want to use adapters that implement the original
interface as well (proxies).  Here is an example that resets an 'approved'
flag whenever new changes are saved.  This proxy could be used, for example, to
mark find new translations to be reviewed and imported.

    >>> class TranslationStoreProxy(object):
    ...     def __init__(self, store):
    ...         self.store = store
    ...     def __getattr_(self, attr):
    ...         return getattr(self.store, attr)
    ...     def __getitem__(self, item):
    ...         return self.store[item]
    ...     def save(self):
    ...         self.store.annotations['approved'] = 'n'
    ...         self.store.save()
    ...     def approved(self):
    ...         return self.store.annotations.get('approved', 'n') == 'y'
    ...     def approve(self):
    ...         self.store.annotations['approved'] = 'y'
    ...         self.store.save()

Some sample usage:

    >>> wrapped_store = TranslationStoreProxy(store)
    >>> wrapped_store.approved()
    False
    >>> wrapped_store.approve()
    >>> wrapped_store.approved()
    True

    >>> wrapped_store[0].trans = [('Unreviewed', 'bogus')]
    >>> wrapped_store.save()

    >>> wrapped_store.approved()
    False

For even more advanced use cases you may want to also wrap translation units
returned by ``makeunit``, ``__getitem__`` and other methods (and unwrap units
passed to ``fill``).  Per-unit version control, access control, etc. can be
implemented this way.

If you know that your adapter/proxy will only be used for the relational
backend, you can gain much efficiency by constructing native SQLAlchemy queries
to access annotations without using the object-relational mapper.  This holds
especially if you need to work with many per-unit annotations because they
can all be selected efficiently with a single query.

The largest disadvantage of proxies is that they do not hook in transparently:
you have to invoke the proxies explicitly.  The storage backend only makes
sure that the data used by proxies persists.
