===================
Translation storage
===================

This package provides an API for storage of software translations.  This file
introduces the capabilities provided by the API and provides some usage
examples.

.. contents::

Getting started
===============

To get started, you need to instantiate a database, by invoking
open_database(uri).  The argument `uri` identifies the type of backend
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

For convenience, translations can be grouped in folders.  The database
contains a reference to the root folder:

    >>> db.root
    <Pootle.storage.rdb.Folder object at ...>

A folder can contain other folders (the ``subfolders`` attribute).  The
``subfolders`` object acts much like standard dictionaries, but instead
of ``__setitem__()`` you should use ``add(key)``, which creates the
folder, attaches it to the parent folder and returns the new object.  This
way all Folder objects are always attached to a hierarchy.

Let's add a subfolder:

    >>> debian_folder = db.root.subfolders.add('debian')
    >>> db.root.subfolders.keys()
    ['debian']

Subfolder objects can be retrieved using ``__getitem__()`` or ``get``:

    >>> db.root.subfolders['debian'] is debian_folder
    True
    >>> db.root.subfolders.get('debian') is debian_folder
    True
    >>> db.root.subfolders.get('bedouin', 'nonexistent')
    'nonexistent'

For convenience, you can retrieve subfolders directly from the folder:

    >>> db.root['debian'] is debian_folder
    True

We can add subfolders into a folder:

    >>> demo_subfolder = debian_folder.subfolders.add('demo')

Modules
-------

Modules define groups of translation strings.  They loosely correspond to
a gettext ``.pot`` file together with all its translations.  Modules are manipulated
pretty much the same way as subfolders:

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

Translation stores correspond to a single gettext ``.pot`` template or a translation
of this template into a particular language.  Modules act as containers for
translation stores.

A translation store's key is the standard ISO639 code of the translation
language, e.g. ``de``, ``lt``, ``fr``.  If necessary, a country's ISO3166
can be appended like this: ``de_DE``, ``pt_BR``, etc.

    >>> store = hello_module.add('lt')
    >>> store
    <Pootle.storage.rdb.TranslationStore object at ...>

Translation units
-----------------

Translation stores contain translation units. A translation unit is a single
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

Language information
--------------------

TODO

Transactions
------------


Adding additional capabilities
==============================

TODO
