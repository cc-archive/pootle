#!/usr/bin/python

import sys
sys.path.append('../..') # in case this module is run directly
import doctest


def test_SimpleMerger():
    """

    We will need a template:

        >>> from Pootle.storage.merge import SimpleMerger
        >>> from Pootle.storage.memory import TranslationStore

        >>> template = TranslationStore('template', object(), None)
        >>> tr1 = template.makeunit([('%d chair', '%d Stuhl'),
        ...                          ('%d chairs', '%d Stuehle')])
        >>> tr2 = template.makeunit([('foo', 'bar')])
        >>> tr3 = template.makeunit([('old', 'old')])
        >>> tr4 = template.makeunit([('new', 'new')])
        >>> template.fill([tr1, tr2, tr3, tr4])

    And a translation object:

        >>> translation = TranslationStore('template', object(), None)
        >>> tr1 = translation.makeunit([('foo', 'not bar')])
        >>> tr2 = translation.makeunit([('%d chair', '%d stool'),
        ...                             ('%d chairs', '%d stools')])
        >>> tr3 = template.makeunit([('new', '')]) # untranslated
        >>> translation.fill([tr1, tr2, tr3])

    Let's do the merge:

        >>> from Pootle.storage.merge import SimpleMerger
        >>> SimpleMerger().merge(translation, template)

        >>> [t.trans for t in translation] #doctest: +NORMALIZE_WHITESPACE
        [[('%d chair', '%d stool'), ('%d chairs', '%d stools')],
         [('foo', 'not bar')],
         [('old', 'old')],
         [('new', 'new')]]

    """


def test_interface():
    """Test conformance to the API interface.

    Poor man's alternative to zope.interface.

        >>> from Pootle.storage.api import validateModule
        >>> import Pootle.storage.merge
        >>> validateModule(Pootle.storage.merge)

    """

if __name__ == '__main__':
    doctest.testmod()
