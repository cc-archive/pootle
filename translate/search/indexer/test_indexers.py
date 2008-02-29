
import __init__ as indexer
import CommonIndexer
import os
import sys

DATABASE = "tmp-index"

# overwrite this value to change the preferred indexing engine
default_engine = "" 

# order of tests to be done
ORDER_OF_TESTS = [ "XapianIndexer", "PyLuceneIndexer" ]


def _get_indexer(location):
    """wrapper around "indexer.get_indexer" to enable a globally preferred
    indexing engine selection

    create an indexer based on the preference order 'default_engine'

    @param location: the path of the database to be created/opened
    @type location: str
    @return: the resulting indexing engine instance
    @rtype: CommonIndexer.CommonDatabase
    """
    return indexer.get_indexer(location, [default_engine])

def clean_database():
    """remove an existing database"""
    dbase_dir = os.path.abspath(DATABASE)
    # the database directory does not exist
    if not os.path.exists(dbase_dir):
        return
    # recursively remove the directory
    for item in os.listdir(dbase_dir):
        os.remove(os.path.join(dbase_dir, item))
    os.rmdir(dbase_dir)

def create_example_content(database):
    """add some defined documents to the database

    this may be used to check some specific queries

    @param database: a indexing database object
    @type database: CommonIndexer.CommonDatabase
    """
    # a reasonable foo-bar entry
    database.index_document(["foo", "bar", "med"])
    # and something more for another document
    database.index_document(["foo", "bar", "HELO"])
    # another similar one - but with "barr" instead of "bar"
    database.index_document(["foo", "barr", "med", "HELO"])
    # some field indexed document data
    database.index_document({"fname1": "foo_field1", "fname2": "foo_field2"})
    database.index_document({"fname1": "bar_field1", "fname2": "foo_field2",
            None: ["HELO", "foo"]})
    database.index_document({ None: "med" })
    assert _get_number_of_docs(database) == 6

def test_create_database():
    """create a new database from scratch"""
    # clean up everything first
    clean_database()
    new_db = _get_indexer(DATABASE)
    assert isinstance(new_db, CommonIndexer.CommonDatabase)
    assert os.path.exists(DATABASE)
    # clean up
    clean_database()

def test_open_database():
    """open an existing database"""
    # clean up everything first
    clean_database()
    # create a new database - it will be closed immediately afterwards
    # since the reference is lost again
    _get_indexer(DATABASE)
    # open the existing database again
    opened_db = _get_indexer(DATABASE)
    assert isinstance(opened_db, CommonIndexer.CommonDatabase)
    # clean up
    clean_database()

def test_make_queries():
    """create a simple query from a plain string"""
    # clean up everything first
    clean_database()
    # initialize the database with example content
    new_db = _get_indexer(DATABASE)
    create_example_content(new_db)
    # plaintext queries
    q_plain1 = new_db.make_query("foo")
    q_plain2 = new_db.make_query("foo bar")
    assert str(q_plain1) != str(q_plain2)
    # list 'and/or'
    q_combined_and = new_db.make_query([new_db.make_query("foo"),
        new_db.make_query("bar")])
    q_combined_or = new_db.make_query([new_db.make_query("foo"),
        new_db.make_query("bar")], require_all=False)
    assert str(q_combined_or) != str(q_combined_and)

def test_partial_text_matching():
    """check if implicit and explicit partial text matching works"""
    # clean up everything first
    clean_database()
    # initialize the database with example content
    new_db = _get_indexer(DATABASE)
    create_example_content(new_db)
    # this query should return two matches (no wildcard by default)
    q_plain_partial1 = new_db.make_query("bar")
    r_plain_partial1 = new_db.get_query_result(q_plain_partial1).get_matches(0,10)
    assert r_plain_partial1[0] == 2
    # this query should return three matches (wildcard works)
    q_plain_partial2 = new_db.make_query("bar", match_text_partial=True)
    r_plain_partial2 = new_db.get_query_result(q_plain_partial2).get_matches(0,10)
    assert r_plain_partial2[0] == 3
    # this query should return two matches (the wildcard is ignored by default)
    q_plain_partial3 = new_db.make_query("bar*")
    r_plain_partial3 = new_db.get_query_result(q_plain_partial3).get_matches(0,10)
    assert r_plain_partial3[0] == 2
    # clean up
    clean_database()


def test_field_matching():
    """test if field specific searching works"""
    # clean up everything first
    clean_database()
    # initialize the database with example content
    new_db = _get_indexer(DATABASE)
    create_example_content(new_db)
    # do a field search with a tuple argument
    q_field1 = new_db.make_query(("fname1", "foo_field1"))
    r_field1 = new_db.get_query_result(q_field1).get_matches(0,10)
    assert r_field1[0] == 1
    # do a field search with a dict argument
    q_field2 = new_db.make_query({"fname1":"bar_field1"})
    r_field2 = new_db.get_query_result(q_field2).get_matches(0,10)
    assert r_field2[0] == 1
    # do an incomplete field search with a dict argument - should fail
    q_field3 = new_db.make_query({"fname1":"foo_field"})
    r_field3 = new_db.get_query_result(q_field3).get_matches(0,10)
    assert r_field3[0] == 0
    # do an AND field search with a dict argument
    q_field4 = new_db.make_query({"fname1":"foo_field1", "fname2":"foo_field2"}, require_all=True)
    r_field4 = new_db.get_query_result(q_field4).get_matches(0,10)
    assert r_field4[0] == 1
    # do an OR field search with a dict argument
    q_field5 = new_db.make_query({"fname1":"foo_field1", "fname2":"foo_field2"}, require_all=False)
    r_field5 = new_db.get_query_result(q_field5).get_matches(0,10)
    assert r_field5[0] == 2
    # do an incomplete field search with a partial field analyzer
    q_field6 = new_db.make_query({"fname1":"foo_field"}, match_text_partial=True)
    r_field6 = new_db.get_query_result(q_field6).get_matches(0,10)
    assert r_field6[0] == 1
    # clean up
    clean_database()

def test_field_analyzers():
    """test if we can change the analyzer of specific fields"""
    # clean up everything first
    clean_database()
    # initialize the database with example content
    new_db = _get_indexer(DATABASE)
    create_example_content(new_db)
    # do an incomplete field search with (default) exact analyzer
    q_field1 = new_db.make_query({"fname1":"bar_field"})
    r_field1 = new_db.get_query_result(q_field1).get_matches(0,10)
    assert r_field1[0] == 0
    # check the get/set field analyzer functions
    assert new_db.get_field_analyzer("fname1") == new_db.ANALYZER_EXACT
    new_db.set_field_analyzers({"fname1":new_db.ANALYZER_PARTIAL})
    assert new_db.get_field_analyzer("fname1") == new_db.ANALYZER_PARTIAL
    # do an incomplete field search - now we use the partial analyzer
    q_field2 = new_db.make_query({"fname1":"bar_field"})
    r_field2 = new_db.get_query_result(q_field2).get_matches(0,10)
    assert r_field2[0] == 1
    # clean up
    clean_database()

def test_and_queries():
    """test if AND queries work as expected"""
    # clean up everything first
    clean_database()
    # initialize the database with example content
    new_db = _get_indexer(DATABASE)
    create_example_content(new_db)
    # do an AND query
    q_and1 = new_db.make_query("foo bar")
    r_and1 = new_db.get_query_result(q_and1).get_matches(0,10)
    assert r_and1[0] == 2
    # do the same AND query in a different way
    q_and2 = new_db.make_query(["foo", "bar"])
    r_and2 = new_db.get_query_result(q_and2).get_matches(0,10)
    assert r_and2[0] == 2
    # do an AND query without results
    q_and3 = new_db.make_query(["HELO", "bar", "med"])
    r_and3 = new_db.get_query_result(q_and3).get_matches(0,10)
    assert r_and3[0] == 0
    # clean up
    clean_database()

def test_or_queries():
    """test if OR queries work as expected"""
    # clean up everything first
    clean_database()
    # initialize the database with example content
    new_db = _get_indexer(DATABASE)
    create_example_content(new_db)
    # do an OR query
    q_or1 = new_db.make_query("foo bar", require_all=False)
    r_or1 = new_db.get_query_result(q_or1).get_matches(0,10)
    assert r_or1[0] == 4
    # do the same or query in a different way
    q_or2 = new_db.make_query(["foo", "bar"], require_all=False)
    r_or2 = new_db.get_query_result(q_or2).get_matches(0,10)
    assert r_or2[0] == r_or1[0]
    # do an OR query with lots of results
    q_or3 = new_db.make_query(["HELO", "bar", "med"], require_all=False)
    r_or3 = new_db.get_query_result(q_or3).get_matches(0,10)
    assert r_or3[0] == 5
    # clean up
    clean_database()

def test_lower_upper_case():
    """test if case is ignored for queries and for indexed terms"""
    # clean up everything first
    clean_database()
    # initialize the database with example content
    new_db = _get_indexer(DATABASE)
    create_example_content(new_db)
    # use upper case search terms for lower case indexed terms
    q_case1 = new_db.make_query("BAR")
    r_case1 = new_db.get_query_result(q_case1).get_matches(0,10)
    assert r_case1[0] == 2
    # use lower case search terms for upper case indexed terms
    q_case2 = new_db.make_query("helo")
    r_case2 = new_db.get_query_result(q_case2).get_matches(0,10)
    assert r_case2[0] == 3
    # use lower case search terms for lower case indexed terms
    q_case3 = new_db.make_query("bar")
    r_case3 = new_db.get_query_result(q_case3).get_matches(0,10)
    assert r_case3[0] == 2
    # use upper case search terms for upper case indexed terms
    q_case4 = new_db.make_query("HELO")
    r_case4 = new_db.get_query_result(q_case4).get_matches(0,10)
    assert r_case4[0] == 3
    # clean up
    clean_database()

def show_database(database=None):
    """print the complete database - for debugging purposes"""
    if hasattr(database, "database"):
        _show_database_xapian(database)
    else:
        _show_database_pylucene(database)


def _show_database_pylucene(database=None):
    reader = database.reader
    for index in range(reader.maxDoc()):
        print reader.document(index)

def _show_database_xapian(database=None):
    import xapian
    doccount = database.database.get_doccount()
    max_doc_index = database.database.get_lastdocid()
    print "Database overview: %d items up to index %d" % (doccount, max_doc_index)
    for index in range(1, max_doc_index+1):
        try:
            document = database.database.get_document(index)
        except xapian.DocNotFoundError:
            continue
        print "\tDocument [%d]: %s" % (index,
                str([one_term.term for one_term in document.termlist()]))


def _get_number_of_docs(database):
    if hasattr(database, "database"):
        # xapian
        return database.database.get_lastdocid()
    else:
        # pylucene
        database.flush()
        return database.reader.numDocs()


if __name__ == "__main__":
    for engine in ORDER_OF_TESTS:
        print "************ running tests for '%s' *****************" % engine
        default_engine = engine
        test_create_database()
        test_open_database()
        test_make_queries()
        test_partial_text_matching()
        test_field_matching()
        test_field_analyzers()
        test_and_queries()
        test_or_queries()
        test_lower_upper_case()
        # TODO: add test for document deletion
        # TODO: add test for transaction handling

