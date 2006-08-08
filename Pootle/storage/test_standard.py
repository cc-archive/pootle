#!/usr/bin/python

import sys
sys.path.append('../..') # in case this module is run directly
import doctest



def test_interface():
    """Test conformance to the API interface.

    Poor man's alternative to zope.interface.

        >>> from Pootle.storage.api import validateModule
        >>> import Pootle.storage.standard
        >>> validateModule(Pootle.storage.standard)

    """


if __name__ == '__main__':
    doctest.testmod()
