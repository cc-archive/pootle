"""
interface for the pylucene indexing engine
"""

__revision__ = "$Id$"

import CommonIndexer
import PyLucene
# TODO: replace this dependency on the jToolkit
import jToolkit.glock
import tempfile
import re


class PyluceneDatabase(CommonIndexer.CommonDatabase):
    """manage and use a pylucene indexing database"""


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
        super(PyluceneDatabase, self).__init__(location)
        self.location = location
        self.analyzer = PyLucene.StandardAnalyzer()
        if os.path.exists(location):
            try:
                # try to open an existing database
                tempreader = PyLucene.IndexReader.open(self.location)
                tempreader.close()
                self.createdIndex = False
            except PyLucene.exceptions.Exception, e:
                # Write an error out, in case this is a real problem instead of an absence of an index
                # TODO: turn the following two lines into debug output
                #errorstr = str(e).strip() + "\n" + self.errorhandler.traceback_str()
                #DEBUG_FOO("could not open index, so going to create: " + errorstr)
                # Create the index, so we can open cached readers on it
                try:
                    tempwriter = PyLucene.IndexWriter(self.location,
                            self.analyzer, True)
                    tempwriter.close()
                    self.createdIndex = True
                except PyLucene.exceptons.Exception, err_msg:
                    raise OSError("Indexer: failed to open or create a Lucene" \
                            + " database (%s): %s" % (self.location, err_msg))
        # the indexer is initialized - now we prepare the searcher
        # create a lock for the database directory - to be used later
        lockname = os.path.join(tempfile.gettempdir(),
                re.sub("\W", "_", self.location))
        self.dir_lock = jToolkit.glock.GlobalLock(lockname)
		# windows file locking seems inconsistent, so we try 10 times
		numtries = 0
        # read "self.indexReader", "self.indexVersion" and "self.indexSearcher"
		try:
			while numtries < 10:
				try:
					self.indexReader = indexer.IndexReader.open(self.location)
					self.indexVersion = self.indexReader.getCurrentVersion(
                            self.location)
					self.indexSearcher = indexer.IndexSearcher(self.indexReader)
					break
                # TODO: replace this with a specific exception
				except Exception, e:
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

    def flush(self, optimize=False):
        """flush the content of the database - to force changes to be written
        to disk

        some databases also support index optimization

        @param optimize: should the index be optimized if possible?
        @type optimize: bool
        """
        if not self._writer_is_open()
            # the indexer is closed - no need to do something
            return
        try:
            if optimize:
                self.writer.optimize()
        finally:
            # close the database even if optimizing failed
            self._writer_close()

    def make_query(self, args, requireall=True, match_text_partial=False):
        """create simple queries (strings or field searches) or
        combine multiple queries (AND/OR)

        To specifiy rules for field searches, you may want to take a look at
        'set_field_analyzers'. The parameter 'match_text_partial' can override
        the previously defined default setting.

        @param args: queries or search string or description of field query
            examples:
                [xapian.Query("foo"), xapian.Query("bar")]
                xapian.Query("foo")
                "bar"
                {"foo": "bar", "foobar": "foo"}
        @type args: list of queries | single query | str | dict
        @param requireall: boolean operator
            (True -> AND (default) / False -> OR)
        @type requireall: boolean
        @param match_partial_text: (only applicable for 'dict' or 'str')
            even partial (truncated at the end) string matches are accepted
            this can override previously defined field analyzer settings
        @type match_partial_text: bool
        @return: the combined query
        @rtype: query type of the specific implemention
        """
        raise NotImplementedError("Incomplete indexer implementation: " \
                + "'make_query' is missing")

    def index_document(self, data):
        """add the given data to the database

        @param data: the data to be indexed.
            A dictionary will be treated as fieldname:value combinations.
            If the fieldname is None then the value will be interpreted as a
            plain term or as a list of plain terms.
            Lists of strings are treated as plain terms.
        @type data: dict | list of str
        """
        raise NotImplementedError("Incomplete indexer implementation: " \
                + "'index_document' is missing")

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

    def get_query_result(self, query):
        """return an object containing the results of a query
        
        @param query: a pre-compiled query
        @type query: a query object of the real implementation
        @return: an object that allows access to the results
        @rtype: subclass of CommonEnquire
        """
        raise NotImplementedError("Incomplete indexer implementation: " \
                + "'get_query_result' is missing")

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
        @type fieldnames: string | list of strings | tuple of strings
        @return: a list of dicts containing the specified field(s)
        @rtype: list of dicts
        """
        raise NotImplementedError("Incomplete indexer implementation: " \
                + "'search' is missing")

    def _writer_open(self):
        """open write access for the indexing database and acquire an
        exclusive lock
        """
        if self.writer is None:
            self.dir_lock.acquire()
            self.writer = PyLucene.IndexWriter(self.location, self.analyzer,
                    False)
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
        # TODO: use a more specific exception
		except Exception,e:
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
            return []
        docs = [ (index, self.enquire.doc(index), self.enquire.id(index), self.enquire.)
                for index in range(start, stop) ]
        result = []
        for index in range(start, stop):
            item = {}
            item["rank"] = index
            item["docid"] = self.enquire.id(index)
            item["percent"] = self.enquire.score(index)
            item["document"] = self.enquire.doc(index)
            result.append(item)
        return (stop-start, self.enquire.length(), result)

