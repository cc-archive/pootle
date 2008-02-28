"""
interface to the xapian indexing engine for pootle
"""

__revision__ = "$Id$"


import CommonIndexer
import xapian
import os
import re


# in xapian there is a length restriction for term strings
# see http://osdir.com/ml/search.xapian.general/2006-11/msg00210.html
# a maximum length of around 240 is described there - but we need less anyway
_MAX_TERM_LENGTH = 128


class XapianDatabase(CommonIndexer.CommonDatabase):
    """interface to the xapian (http://xapian.org) indexer
    """

    QUERY_TYPE = xapian.Query

    def __init__(self, location):
        """initialize or open a xapian database

        The following exceptions can be raised:
            ValueError: the given location exists, but the database type
                is incompatible (e.g. created by a different indexing engine)
            OSError: the database failed to initialize

        @param location: the path to the database (usually a directory)
        @type location: str
        @throws: OSError, ValueError
        """
        # call the __init__ function of our parent
        super(XapianDatabase, self).__init__(location)
        self.location = location
        if os.path.exists(location):
            # try to open an existing database
            try:
                self.database = xapian.WritableDatabase(self.location,
                    xapian.DB_OPEN)
            except xapian.DatabaseOpeningError, err_msg:
                raise ValueError("Indexer: failed to open xapian database " \
                        + "(%s) - maybe it is not a xapian database: %s" \
                        % (self.location, err_msg))
        else:
            # create a new database
            try:
                self.database = xapian.WritableDatabase(self.location,
                        xapian.DB_CREATE_OR_OPEN)
            except xapian.DatabaseOpeningError, err_msg:
                raise OSError("Indexer: failed to open or create a xapian " \
                        + "database (%s): %s" % (self.location, err_msg))

    def flush(self, optimize=False):
        """force to write the current changes to disk immediately

        @param optimize: ignored for xapian
        @type optimize: bool
        """
        # write changes to disk (only if database is read-write)
        if (isinstance(self.database, xapian.WritableDatabase)):
            self.database.flush()
        # free the database to remove locks - this is a xapian-specific issue
        self.database = None
        # reopen it as read-only
        self._prepare_database()

    def _create_query_for_query(self, query):
        """generate a query based on an existing query object

        basically this function should just create a copy of the original
        
        @param query: the original query object
        @type query: xapian.Query
        @return: the resulting query object
        @rtype: xapian.Query
        """
        # create a copy of the original query
        return xapian.Query(query)

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
        @param analyzer: the analyzer to be used
            possible analyzers are:
                CommonDatabase.ANALYZER_EXACT (default)
                    the field value must excactly match the query string
                CommonDatabase.ANALYZER_PARTIAL
                    the field value must start with the query string
        @type analyzer: bool
        @return: resulting query object
        @rtype: xapian.Query
        """
        qp = xapian.QueryParser()
        qp.set_database(self.database)
        if require_all:
            qp.set_default_op(xapian.Query.OP_AND)
        else:
            qp.set_default_op(xapian.Query.OP_OR)
        if (analyzer == self.ANALYZER_EXACT) or (analyzer is None):
            match_flags = 0
        elif analyzer == self.ANALYZER_PARTIAL:
            match_flags = xapian.QueryParser.FLAG_PARTIAL
        else:
            # invalid matching returned - maybe the field's default
            # analyzer is broken?
            raise ValueError("unknown analyzer: %d" % analyzer)
        return qp.parse_query(text, match_flags)

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
        @return: the resulting query object
        @rtype: xapian.Query
        """
        qp = xapian.QueryParser()
        qp.set_database(self.database)
        if analyzer == self.ANALYZER_EXACT:
            match_flags = 0
        elif analyzer == self.ANALYZER_PARTIAL:
            match_flags = xapian.QueryParser.FLAG_PARTIAL
        else:
            # invalid matching returned - maybe the field's default
            # analyzer is broken?
            raise ValueError("unknown analyzer selected (%d) " % analyzer \
                    + "for field '%s'" % field)
        # escape the query string and truncate if necessary
        match_string = _escape_term_value(value)
        match_string = _truncate_term_length(match_string, len(field)+1)
        # we search for a string with "field:" as default prefix
        return qp.parse_query(match_string, match_flags, "%s:" % field)

    def _create_query_combined(self, queries, require_all=True):
        """generate a combined query

        @param queries: list of the original queries
        @type queries: list of xapian.Query
        @param require_all: boolean operator
            (True -> AND (default) / False -> OR)
        @type require_all: bool
        @return: the resulting combined query object
        @rtype: xapian.Query
        """
        if require_all:
            query_op = xapian.Query.OP_AND
        else:
            query_op = xapian.Query.OP_OR
        return xapian.Query(query_op, queries)

    def index_document(self, data):
        """add the given data to the database

        @param data: the data to be indexed.
            A dictionary will be treated as fieldname:value combinations.
            If the fieldname is None then the value will be interpreted as a
            plain term or as a list of plain terms.
            Lists of strings are treated as plain terms.
        @type data: dict | list of str
        """
        # open the database for writing
        self._prepare_database(writable=True)
        doc = xapian.Document()
        if isinstance(data, dict):
            data = data.items()
        # add all data
        for dataset in data:
            if isinstance(dataset, tuple):
                # the dataset tuple consists of '(key, value)'
                key, value = dataset
                if key is None:
                    if isinstance(value, list):
                        terms = value[:]
                    elif isinstance(value, str):
                        terms = [value]
                    else:
                        raise ValueError("Invalid data type to be indexed: %s" \
                                % str(type(data)))
                    for one_term in terms:
                        doc.add_term(_truncate_term_length(_escape_term_value(
                            one_term)))
                else:
                    # cut the length if necessary
                    doc.add_term(_truncate_term_length("%s:%s" % \
                            (key, _escape_term_value(value))))
            elif isinstance(dataset, str):
                doc.add_term(_truncate_term_length(_escape_term_value(
                        dataset)))
            else:
                raise ValueError("Invalid data type to be indexed: %s" \
                        % str(type(data)))
        self.database.add_document(doc)

    def begin_transaction(self):
        """begin a transaction

        Xapian supports transactions to group multiple database modifications.
        This avoids intermediate flushing and therefore increases performance.
        """
        self._prepare_database(writable=True)
        self.database.begin_transaction()

    def cancel_transaction(self):
        """cancel an ongoing transaction

        no changes since the last execution of 'begin_transcation' are written
        """
        self._prepare_database(writable=True)
        self.database.cancel_transaction()

    def commit_transaction(self):
        """submit the changes of an ongoing transaction

        all changes since the last execution of 'begin_transaction' are written
        """
        self._prepare_database(writable=True)
        self.database.commit_transaction()

    def get_query_result(self, query):
        """return an object containing the results of a query
        
        @param query: a pre-compiled xapian query
        @type query: xapian.Query
        @return: an object that allows access to the results
        @rtype: XapianIndexer.CommonEnquire
        """
        enquire = xapian.Enquire(self.database)
        enquire.set_query(query)
        return XapianEnquire(enquire)

    def delete_document_by_id(self, docid):
        """delete a specified document

        @param docid: the document ID to be deleted
        @type docid: int
        """
        # open the database for writing
        self._prepare_database(writable=True)
        try:
            self.database.delete_document(docid)
            return True
        except xapian.DocNotFoundError:
            return False

    def search(self, query, fieldnames):
        """return a list of the contents of specified fields for all matches of
        a query

        @param query: the query to be issued
        @type query: xapian.Query
        @param fieldnames: the name(s) of a field of the document content
        @type fieldnames: string | list of strings | tuple of strings
        @return: a list of dicts containing the specified field(s)
        @rtype: list of dicts
        """
        result = []
        if isinstance(fieldnames, str):
            fieldnames = [fieldnames]
        def extract_fieldvalue(match):
            """return lists of dicts of field values"""
            item_fields = {}
            for term in match["document"].termlist():
                for fname in fieldnames:
                    if term.term.startswith("%s:" % fname):
                        # extract the remaining string
                        item_fields[fname] = term.term[len(fname)+1:]
            result.append(item_fields)
        self._walk_matches(query, extract_fieldvalue)
        return result

    def _prepare_database(self, writable=False):
        """reopen the database as read-only or as writable if necessary

        this fixes a xapian specific issue regarding open locks for
        writable databases

        @param writable: True for opening a writable database
        @type writable: bool
        """
        if writable and (not isinstance(self.database,
                xapian.WritableDatabase)):
            self.database = xapian.WritableDatabase(self.location,
                    xapian.DB_OPEN)
        elif not writable and (not isinstance(self.database, xapian.Database)):
            self.database = xapian.Database(self.location)


class XapianEnquire(CommonIndexer.CommonEnquire):
    """interface to the xapian object for storing sets of matches
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
        matches = self.enquire.get_mset(start, number)
        result = []
        for match in matches:
            elem = {}
            elem["rank"] = match[xapian.MSET_RANK]
            elem["docid"] = match[xapian.MSET_DID]
            elem["percent"] = match[xapian.MSET_PERCENT]
            elem["document"] = match[xapian.MSET_DOCUMENT]
            result.append(elem)
        return (matches.size(), matches.get_matches_estimated(), result)


def _truncate_term_length(term, taken=0):
    """truncate the length of a term string length to the maximum allowed
    for xapian terms

    @param term: the value of the term, that should be truncated
    @type term: str
    @param taken: since a term consists of the name of the term and its
        actual value, this additional parameter can be used to reduce the
        maximum count of possible characters
    @type taken: int
    @return: the truncated string
    @rtype: str
    """
    if len(term) > _MAX_TERM_LENGTH - taken:
        return term[0:_MAX_TERM_LENGTH - taken - 1]
    else:
        return term

def _escape_term_value(term):
    """replace invalid characters of a term value with a safe character

    This escaping is not reversible, thus it could possibly lead to collisions.
    Since these collisions do not seem to be relevant, it should be safe to
    ignore them.
    
    @param term: the term value to be escaped
    @type term: str
    @return: the escaped term string
    @rtype: str
    """
    # replace non-alphanumeric characters with an underscore
    # only lower case - queries are turned to lower case, too
    return re.sub(u"\W", "_", term).lower()

