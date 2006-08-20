"""General tests."""

import sys
import unittest
import doctest

modules = ['ddtp', 'memory', 'merge', 'po', 'rdb', 'standard']
flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)


def test_suite():
    suites = [doctest.DocTestSuite('Pootle.storage.test_%s' % module,
                                   optionflags=flags)
              for module in modules]
    suites.append(doctest.DocFileSuite('README.txt', optionflags=flags))
    return unittest.TestSuite(suites)

if __name__ == '__main__':
    sys.path.append('../..') # in case this module is run directly
    unittest.main(defaultTest='test_suite')

