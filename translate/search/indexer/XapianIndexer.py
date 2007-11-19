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
        if os.path.exists(location):
            # try to open an existing database
            try:
                self.database = xapian.WritableDatabase(location,
                    xapian.DB_OPEN)
            except xapian.DatabaseOpeningError, err_msg:
                raise ValueError("Indexer: failed to open xapian database " \
                        + "(%s) - maybe it is not a xapian database: %s" \
                        % (location, err_msg))
        else:
            # create a new database
            try:
                self.database = xapian.WritableDatabase(location,
                        xapian.DB_CREATE_OR_OPEN)
            except xapian.DatabaseOpeningError, err_msg:
                raise OSError("Indexer: failed to open or create a xapian " \
                        + "database (%s): %s" % (location, err_msg))

    def flush(self, optimize=False):
        """force to write the current changes to disk immediately

        @param optimize: ignored for xapian
        @type optimize: bool
        """
        self.database.flush()

    def make_query(self, args, requireall=True, match_text_partial=None):
        """create simple queries (strings or field searches) or
        combine multiple queries (AND/OR)

        To specifiy rules for field searches, you may want to take a look at
        'set_field_analyzers'. The parameter 'match_text_partial' can override
        the previously defined default.

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
        @rtype: xapian.Query
        """
        # evaluate the 'requireall' setting
        if requireall:
            query_op = xapian.Query.OP_AND
        else:
            query_op = xapian.Query.OP_OR
        # turn a dict into a list if necessary
        if isinstance(args, dict):
            args = args.items()
        # turn 'args' into a list if necessary
        if not isinstance(args, list):
            args = [args]
        # for some cases we need a parser - sometimes even bound to a database
        # e.g. for partial string matching
        qp = xapian.QueryParser()
        qp.set_database(self.database)
        # combine all given queries
        result = []
        for query in args:
            # just add precompiled queries
            if isinstance(query, xapian.Query):
                result.append(query)
            # create field/value queries out of a tuple
            elif isinstance(query, tuple):
                field, value = query
                # check for the choosen match type ('exact' or 'partial')
                match_type = None
                if (match_text_partial is True):
                    match_type = self.ANALYZER_PARTIAL
                elif (match_text_partial is False):
                    match_type = self.ANALYZER_EXACT
                else:
                    match_type = self.get_field_analyzer(field)
                # escape the query string and truncate if necessary
                match_string = _truncate_term_length(_escape_term_value(value),
                        len(field)+1)
                # determine necessary options for parsing
                if match_type == self.ANALYZER_EXACT:
                    # no special flags are necessary
                    match_flags = 0
                elif match_type == self.ANALYZER_PARTIAL:
                    # me need the flag for partial matches
                    match_flags = xapian.QueryParser.FLAG_PARTIAL
                else:
                    # invalid matching returned - maybe the field's default
                    # analyzer is broken?
                    raise ValueError("unknown analyzer selected (%d) " \
                            % match_type + "for field '%s'" % field)
                # add the new query to the list of to-be-combined queries
                result.append(qp.parse_query(match_string, match_flags,
                    "%s:" % field))
            # parse plaintext queries
            elif isinstance(query, str):
                if match_text_partial is True:
                    # partial string matching
                    result.append(qp.parse_query(query,
                            xapian.QueryParser.FLAG_PARTIAL))
                else:
                    # exact string matching
                    result.append(qp.parse_query(query))
            else:
                # other types of queries are not supported
                raise ValueError("Unable to handle query type: %s" \
                        % str(type(query)))
        # return the combined query
        return xapian.Query(query_op, result)

    def index_data(self, data):
        """add the given data to the database

        @param data: the data to be indexed
        @type data: dict | list of tuples
        """
        # for lists: call this function for each element in the list
        if isinstance(data, list) and isinstance(data[0], dict):
            for one_doc in data:
                self.index_data(one_doc)
        else:
            # turn a dictionary into a list of tuples, if necessary
            if isinstance(data, dict):
                data = data.items()
            doc = xapian.Document()
            # add all data
            for dataset in data:
                if isinstance(dataset, tuple):
                    # the dataset tuple consists of '(key, value)'
                    key, value = dataset
                    # cut the length if necessary
                    doc.add_term(_truncate_term_length("%s:%s" % \
                            (key, _escape_term_value(value))))
                else:
                    raise ValueError("Invalid data type to be indexed: %s" \
                            % str(type(data)))
            self.database.add_document(doc)

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
    return re.sub(u"\W", "_", term)

