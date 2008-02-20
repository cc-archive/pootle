"""
interface for differrent indexing engines for pootle

"""

# TODO:
#   unittests
#   interface for PyLucene

__revision__ = "$Id$"

import CommonIndexer
import os


def _get_available_indexers():
    """get a list of the available supported indexing engines

    search through the translate.search.indexer package for modules derived from
    the CommonIndexer class
    """
    result = []
    # get the package directory
    indexer_dir = os.path.dirname(os.path.abspath(__file__))
    # sort the files in the directory by name - to make it determinable,
    # which indexing engine is chosen in case of multiple possibilities
    all_files = os.listdir(indexer_dir)
    all_files.sort()
    for mod_file in all_files:
        if mod_file == __file__:
            # we should not import ourself
            continue
        mod_path = os.path.join(indexer_dir, mod_file)
        if (not mod_path.endswith(".py")) or (not os.path.isfile(mod_path)) \
                or (not os.access(mod_path, os.R_OK)):
            # no file / wrong extension / not readable -> skip it
            continue
        # strip the ".py" prefix
        mod_name = mod_file[:-3]
        # TODO - debug: "[Indexer]: trying to import indexing engines from '%s'" % mod_path
        try:
            module = __import__(mod_name, globals(), {})
        except ImportError:
            # maybe it is unusable or dependencies are missing
            continue
        for item in dir(module):
            try:
                element = getattr(module, item)
            except TypeError:
                # this rarely happens: e.g. for 'item' being 'None'
                continue
            try:
                # the class must inherit CommonDatabase (without being the same)
                if issubclass(element, CommonIndexer.CommonDatabase) \
                        and not element is CommonIndexer.CommonDatabase:
                    # TODO: debug - "[Indexer]: indexing engine found in '%s': %s" % (mod_path, element)
                    result.append(element)
            except TypeError:
                # 'element' is not a class
                continue
    return result


# store the available indexers - this is done only once during the first import
_AVAILABLE_INDEXERS = _get_available_indexers()

# True for a not-empty list - this should be used to check if indexing support
# is available
HAVE_INDEXER = bool(_AVAILABLE_INDEXERS)


def get_indexer(location):
    """return an appropriate indexer for the given directory

    If the directory already exists, then we check, if one of the available
    indexers knows how to handle it. Otherwise we return the first available
    indexer.

    The following exceptions can be thrown:
        IndexError: there is no indexing engine available
        ValueError: the database location already exists, but we did not find
            a suitable indexing engine for it
        OSError: any error that could occour while creating or opening the
            database

    @param location: the directory where the indexing database should be stored
    @type location: string
    @return: the class of the most appropriate indexer
    @rtype: subclass of CommonIndexer.CommonDatabase
    @throws: ValueError, OSError
    """
    if not _AVAILABLE_INDEXERS:
        raise IndexError("Indexer: no indexing engines are available")
    if os.path.exists(location):
        for index_class in _AVAILABLE_INDEXERS:
            try:
                # the first match is sufficient
                return index_class(location)
            except (ValueError, OSError):
                # invalid type of database or some other error
                continue
    # the database does not exist yet or we did not find an appropriate
    # class that can handle it - so we just take the first available
    # indexing engine
    # this may result in a ValueError or an OSError
    return _AVAILABLE_INDEXERS[0](location)


if __name__ == "__main__":
    # show all supported indexing engines (with fulfilled requirements)
    for ONE_INDEX in _AVAILABLE_INDEXERS:
        print ONE_INDEX

