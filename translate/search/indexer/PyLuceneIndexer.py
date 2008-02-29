"""
interface for the PyLucene (v2.x) indexing engine

take a look at PyLuceneIndexer1.py for the PyLucene v1.x interface
"""

__revision__ = "$Id$"

import CommonIndexer
import PyLucene
# TODO: replace this dependency on the jToolkit
import jToolkit.glock
import tempfile
import re
import os
import time


UNNAMED_FIELD_NAME = "FieldWithoutAName"
MAX_FIELD_SIZE = 1048576


def is_available():
    return _get_pylucene_version() == 2


class PyLuceneDatabase(CommonIndexer.CommonDatabase):
    """manage and use a pylucene indexing database"""

    QUERY_TYPE = PyLucene.Query

    def __init__(self, location):
        """initialize or open an indexing database

        Any derived class must override __init__.

        The following exceptions can be raised:
            ValueError: the given location exists, but the database type
                is incompatible (e.g. created by a different indexing engine)
            OSError: the database failed to initialize

        @param location: the path to the database (usually a directory)
        @type location: str
        @throws: OSError, ValueError
        """
        super(PyLuceneDatabase, self).__init__(location)
        self.location = location
        self.analyzer = PyLucene.StandardAnalyzer()
        self.writer = None
        self.reader = None
        self.index_version = None
        try:
            # try to open an existing database
            tempreader = PyLucene.IndexReader.open(self.location)
            tempreader.close()
        except PyLucene.JavaError, err_msg:
            # Write an error out, in case this is a real problem instead of an absence of an index
            # TODO: turn the following two lines into debug output
            #errorstr = str(e).strip() + "\n" + self.errorhandler.traceback_str()
            #DEBUG_FOO("could not open index, so going to create: " + errorstr)
            # Create the index, so we can open cached readers on it
            try:
                tempwriter = PyLucene.IndexWriter(self.location,
                        self.analyzer, True)
                tempwriter.close()
            except PyLucene.JavaError, err_msg:
                raise OSError("Indexer: failed to open or create a Lucene" \
                        + " database (%s): %s" % (self.location, err_msg))
        # the indexer is initialized - now we prepare the searcher
        # create a lock for the database directory - to be used later
        lockname = os.path.join(tempfile.gettempdir(),
                re.sub("\W", "_", self.location))
        self.dir_lock = jToolkit.glock.GlobalLock(lockname)
        # windows file locking seems inconsistent, so we try 10 times
        numtries = 0
        self.dir_lock.acquire(blocking=True)
        # read "self.reader", "self.indexVersion" and "self.searcher"
        try:
            while numtries < 10:
                try:
                    self.reader = PyLucene.IndexReader.open(self.location)
                    self.indexVersion = self.reader.getCurrentVersion(
                            self.location)
                    self.searcher = PyLucene.IndexSearcher(self.reader)
                    break
                except PyLucene.JavaError, e:
                    # store error message for possible later re-raise (below)
                    lock_error_msg = e
                    time.sleep(0.01)
                numtries += 1
            else:
                # locking failed for 10 times
                raise OSError("Indexer: failed to lock index database" \
                        + " (%s)" % lock_error_msg)
        finally:
            self.dir_lock.release()
        # initialize the searcher and the reader
        self._index_refresh()

    def __del__(self):
        """remove lock and close writer after loosing the last reference"""
        self._writer_close()

    def flush(self, optimize=False):
        """flush the content of the database - to force changes to be written
        to disk

        some databases also support index optimization

        @param optimize: should the index be optimized if possible?
        @type optimize: bool
        """
        if not self._writer_is_open():
            # the indexer is closed - no need to do something
            return
        try:
            if optimize:
                self.writer.optimize()
        finally:
            # close the database even if optimizing failed
            self._writer_close()
            # the reader/searcher needs an update, too
            self._index_refresh()

    def _create_query_for_query(self, query):
        """generate a query based on an existing query object

        basically this function should just create a copy of the original
        
        @param query: the original query object
        @type query: PyLucene.Query
        @return: resulting query object
        @rtype: PyLucene.Query
        """
        # TODO: a deep copy or a clone would be safer
        # somehow not working (returns "null"): copy.deepcopy(query)
        return query

    def _create_query_for_string(self, text, require_all=True,
            analyzer=None):
        """generate a query for a plain term of a string query

        basically this function parses the string and returns the resulting
        query

        @param text: the query string
        @type text: str
        @param require_all: boolean operator
            (True -> AND (default) / False -> OR)
        @type require_all: bool
        @return: resulting query object
        @rtype: PyLucene.Query
        """
        text = _escape_term_value(text)
        qp = PyLucene.QueryParser(UNNAMED_FIELD_NAME,
                PyLucene.StandardAnalyzer())
        if analyzer == self.ANALYZER_EXACT:
            pass
        elif analyzer == self.ANALYZER_PARTIAL:
            # PyLucene uses explicit wildcards for partial matching
            text += "*"
        if require_all:
            qp.setDefaultOperator(qp.Operator.AND)
        else:
            qp.setDefaultOperator(qp.Operator.OR)
        return qp.parse(text)

    def _create_query_for_field(self, field, value, analyzer=None):
        """generate a field query

        this functions creates a field->value query

        @param field: the fieldname to be used
        @type field: str
        @param value: the wanted value of the field
        @type value: str
        @param analyzer: the analyzer to be used
            possible analyzers are:
                CommonDatabase.ANALYZER_EXACT (default)
                    the field value must excactly match the query string
                CommonDatabase.ANALYZER_PARTIAL
                    the field value must start with the query string
        @type analyzer: bool
        @return: resulting query object
        @rtype: PyLucene.Query
        """
        value = _escape_term_value(value)
        if analyzer == self.ANALYZER_EXACT:
            pass
        elif analyzer == self.ANALYZER_PARTIAL:
            # PyLucene uses explicit wildcards for partial matching
            value += "*"
        else:
            # invalid matching returned - maybe the field's default
            # analyzer is broken?
            raise ValueError("unknown analyzer selected (%d) " % analyzer \
                    + "for field '%s'" % field)
        return PyLucene.QueryParser(field,
                PyLucene.StandardAnalyzer()).parse(value)

    def _create_query_combined(self, queries, require_all=True):
        """generate a combined query

        @param queries: list of the original queries
        @type queries: list of PyLucene.Query
        @param require_all: boolean operator
            (True -> AND (default) / False -> OR)
        @type require_all: bool
        @return: the resulting combined query object
        @rtype: PyLucene.Query
        """
        combined_query = PyLucene.BooleanQuery()
        for query in queries:
            combined_query.add(
                    PyLucene.BooleanClause(query, _occur(require_all, False)))
        return combined_query

    def _create_empty_document(self):
        """create an empty document to be filled and added to the index later

        @return: the new document object
        @rtype: PyLucene.Document
        """
        return PyLucene.Document()
    
    def _add_plain_term(self, document, term):
        """add a term to a document

        @param document: the document to be changed
        @type document: PyLucene.Document
        @param term: a single term to be added
        @type term: str
        """
        document.add(PyLucene.Field(str(UNNAMED_FIELD_NAME), term,
                PyLucene.Field.Store.YES, PyLucene.Field.Index.TOKENIZED))

    def _add_field_term(self, document, field, term):
        """add a field term to a document

        @param document: the document to be changed
        @type document: PyLucene.Document
        @param field: name of the field
        @type field: str
        @param term: term to be associated to the field
        @type term: str
        """
        # TODO: decoding (utf-8) is missing
        document.add(PyLucene.Field(str(field), str(term),
                PyLucene.Field.Store.YES, PyLucene.Field.Index.TOKENIZED))

    def _add_document_to_index(self, document):
        """add a prepared document to the index database

        @param document: the document to be added
        @type document: PyLucene.Document
        """
        self._writer_open()
        self.writer.addDocument(document)

    def begin_transaction(self):
        """PyLucene does not support transactions

        Thus this function just opens the database for write access.
        Call "cancel_transaction" or "commit_transaction" to close write
        access in order to remove the exclusive lock from the database
        directory.
        """
        self._writer_open()

    def cancel_transaction(self):
        """PyLucene does not support transactions

        Thus this function just closes the database write access and removes
        the exclusive lock.

        See 'start_transaction' for details.
        """
        self._writer_close()

    def commit_transaction(self):
        """PyLucene does not support transactions

        Thus this function just closes the database write access and removes
        the exclusive lock.

        See 'start_transaction' for details.
        """
        self._writer_close()
        self.flush()

    def get_query_result(self, query):
        """return an object containing the results of a query
        
        @param query: a pre-compiled query
        @type query: a query object of the real implementation
        @return: an object that allows access to the results
        @rtype: subclass of CommonEnquire
        """
        return PyLuceneHits(self.searcher.search(query))

    def delete_document_by_id(self, docid):
        """delete a specified document

        @param docid: the document ID to be deleted
        @type docid: int
        """
        self.reader.deleteDocument(docid)
        # TODO: check the performance impact of calling "refresh" for each id
        self._index_refresh()

    def search(self, query, fieldnames):
        """return a list of the contents of specified fields for all matches of
        a query

        @param query: the query to be issued
        @type query: a query object of the real implementation
        @param fieldnames: the name(s) of a field of the document content
        @type fieldnames: string | list of strings
        @return: a list of dicts containing the specified field(s)
        @rtype: list of dicts
        """
        if isinstance(fieldnames, str):
            fieldnames = [fieldnames]
        hits = PyLucene.searcher.search(query)
        result = []
        for hit, doc in hits:
            fields = {}
            for fieldname in fieldnames:
                content = doc.get(fieldname)
                if not content is None:
                    fields[fieldname] = content
            result.append(fields)
        return result

    def _writer_open(self):
        """open write access for the indexing database and acquire an
        exclusive lock
        """
        if self.writer is None:
            self.dir_lock.acquire()
            self.writer = PyLucene.IndexWriter(self.location, self.analyzer,
                    False)
            # "setMaxFieldLength" is available since PyLucene v2
            # we must stay compatible to v1 for the derived class
            # (PyLuceneIndexer1) - thus we make this step optional
            if hasattr(self.writer, "setMaxFieldLength"):
                self.writer.setMaxFieldLength(MAX_FIELD_SIZE)
        # do nothing, if it is already open

    def _writer_close(self):
        """close indexing write access and remove the database lock"""
        if self.writer is None:
            # do nothing, if it is already closed
            return
        self.writer.close()
        self.writer = None
        self.dir_lock.release()
        # just to make sure that the lock is removed
        self.dir_lock.forcerelease()

    def _writer_is_open(self):
        """check if the indexing write access is currently open"""
        return not self.writer is None

    def _index_refresh(self):
        """re-read the indexer database"""
        try:
            self.dir_lock.acquire(blocking=False)
        except jToolkit.glock.GlobalLockError, e:
            # if this fails the index is being rewritten, so we continue with
            # our old version
            return
        try:
            if self.reader is None or self.searcher is None:
                self.reader = PyLucene.IndexReader.open(self.location)
                self.searcher = PyLucene.IndexSearcher(self.reader)
            elif self.index_version != self.reader.getCurrentVersion( \
                    self.location):
                self.searcher.close()
                self.reader.close()
                self.reader = PyLucene.IndexReader.open(self.location)
                self.searcher = PyLucene.IndexSearcher(self.reader)
                self.index_version = self.reader.getCurrentVersion(self.location)
        except PyLucene.JavaError,e:
            # TODO: add some debugging output?
            #self.errorhandler.logerror("Error attempting to read index - try reindexing: "+str(e))
            pass
        self.dir_lock.release()


class PyLuceneHits(CommonIndexer.CommonEnquire):
    """an enquire object contains the information about the result of a request
    """

    def get_matches(self, start, number):
        """return a specified number of qualified matches of a previous query

        @param start: the index of the first match to return
        @type start: int
        @param number: the number of matching entries to return
        @type number: int
        @return: a set of matching entries and some statistics
        @rtype: tuple of (returned number, available number, matches)
                "matches" is a dictionary of
                    ["rank", "percent", "document", "docid"]
        """
        # check if requested results do not exist
        # stop is the lowest index number to be ommitted
        stop = start + number
        if stop > self.enquire.length():
            stop = self.enquire.length()
        # invalid request range
        if stop <= start:
            return (0, self.enquire.length(), [])
        result = []
        for index in range(start, stop):
            item = {}
            item["rank"] = index
            item["docid"] = self.enquire.id(index)
            item["percent"] = self.enquire.score(index)
            item["document"] = self.enquire.doc(index)
            result.append(item)
        return (stop-start, self.enquire.length(), result)

def _occur(required, prohibited):
       if required == True and prohibited == False:
           return PyLucene.BooleanClause.Occur.MUST
       elif required == False and prohibited == False:
           return PyLucene.BooleanClause.Occur.SHOULD
       elif required == False and prohibited == True:
           return PyLucene.BooleanClause.Occur.MUST_NOT
       else:
           # It is an error to specify a clause as both required
           # and prohibited
           return None

def _get_pylucene_version():
    """get the installed pylucene version

    @return: 1 -> PyLucene v1.x / 2 -> PyLucene v2.x / 0 -> unknown
    @rtype: int
    """
    version = PyLucene.LUCENE_VERSION
    if version.startswith("1."):
        return 1
    elif version.startswith("2."):
        return 2
    else:
        return 0


def _escape_term_value(text):
    return re.sub("\*", "", text)

