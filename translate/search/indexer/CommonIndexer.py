"""
base class for interfaces to indexing engines for pootle
"""

__revision__ = "$Id$"


def is_available():
    """check if this indexing engine interface is usable

    this function must exist in every module that contains indexing engine
    interfaces

    @return: is this interface usable?
    @rtype: bool
    """
    return False


class CommonDatabase(object):
    """base class for indexing support

    any real implementation must override most methods of this class
    """

    field_analyzers = {}
    """mapping of field names and analyzers - see 'set_field_analyzers'"""

    ANALYZER_EXACT = 0
    """exact matching: the query string must equal the whole term string"""

    ANALYZER_PARTIAL = 1
    """partial matching: a document matches, even if the query string only
    matches the beginning of the term value"""

    QUERY_TYPE = None

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
        self.field_analyzers = {}
        # just do some checks
        if self.QUERY_TYPE is None:
            raise NotImplementedError("Incomplete indexer implementation: " \
                    + "'QUERY_TYPE' is undefined")

    def flush(self, optimize=False):
        """flush the content of the database - to force changes to be written
        to disk

        some databases also support index optimization

        @param optimize: should the index be optimized if possible?
        @type optimize: bool
        """
        raise NotImplementedError("Incomplete indexer implementation: " \
                + "'flush' is missing")

    def make_query(self, args, require_all=True, match_text_partial=None):
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
        @param require_all: boolean operator
            (True -> AND (default) / False -> OR)
        @type require_all: boolean
        @param match_partial_text: (only applicable for 'dict' or 'str')
            even partial (truncated at the end) string matches are accepted
            this can override previously defined field analyzer settings
        @type match_partial_text: bool
        @return: the combined query
        @rtype: query type of the specific implemention
        """
        # turn a dict into a list if necessary
        if isinstance(args, dict):
            args = args.items()
        # turn 'args' into a list if necessary
        if not isinstance(args, list):
            args = [args]
        # combine all given queries
        result = []
        for query in args:
            # just add precompiled queries
            if isinstance(query, self.QUERY_TYPE):
                result.append(self._create_query_for_query(query))
            # create field/value queries out of a tuple
            elif isinstance(query, tuple):
                field, value = query
                # check for the choosen match type ('exact' or 'partial')
                match_type = None
                if match_text_partial is True:
                    analyzer = self.ANALYZER_PARTIAL
                elif match_text_partial is False:
                    analyzer = self.ANALYZER_EXACT
                else:
                    analyzer = self.get_field_analyzers(field)
                result.append(self._create_query_for_field(field, value,
                        analyzer=analyzer))
            # parse plaintext queries
            elif isinstance(query, str):
                if match_text_partial is True:
                    analyzer = self.ANALYZER_PARTIAL
                else:
                    analyzer = self.ANALYZER_EXACT
                result.append(self._create_query_for_string(query,
                        require_all=require_all, analyzer=analyzer))
            else:
                # other types of queries are not supported
                raise ValueError("Unable to handle query type: %s" \
                        % str(type(query)))
        # return the combined query
        return self._create_query_combined(result, require_all)

    def _create_query_for_query(self, query):
        """generate a query based on an existing query object

        basically this function should just create a copy of the original
        
        @param query: the original query object
        @type query: xapian.Query
        @return: the resulting query object
        @rtype: xapian.Query | PyLucene.Query
        """
        raise NotImplementedError("Incomplete indexer implementation: " \
                + "'_create_query_for_query' is missing")

    def _create_query_for_string(self, text, require_all=True,
            match_text_partial=None):
        """generate a query for a plain term of a string query

        basically this function parses the string and returns the resulting
        query

        @param text: the query string
        @type text: str
        @param require_all: boolean operator
            (True -> AND (default) / False -> OR)
        @type require_all: bool
        @return: resulting query object
        @rtype: xapian.Query | PyLucene.Query
        """
        raise NotImplementedError("Incomplete indexer implementation: " \
                + "'_create_query_for_string' is missing")

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
        @rtype: xapian.Query | PyLucene.Query
        """
        raise NotImplementedError("Incomplete indexer implementation: " \
                + "'_create_query_for_field' is missing")

    def _create_query_combined(self, queries, require_all=True):
        """generate a combined query

        @param queries: list of the original queries
        @type queries: list of xapian.Query
        @param require_all: boolean operator
            (True -> AND (default) / False -> OR)
        @type require_all: bool
        @return: the resulting combined query object
        @rtype: xapian.Query | PyLucene.Query
        """
        raise NotImplementedError("Incomplete indexer implementation: " \
                + "'_create_query_combined' is missing")

    def index_document(self, data):
        """add the given data to the database

        @param data: the data to be indexed.
            A dictionary will be treated as fieldname:value combinations.
            If the fieldname is None then the value will be interpreted as a
            plain term or as a list of plain terms.
            Lists of strings are treated as plain terms.
        @type data: dict | list of str
        """
        doc = self._create_empty_document()
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
                        self._add_plain_term(doc, one_term)
                else:
                    self._add_field_term(doc, key, value)
            elif isinstance(dataset, str):
                self._add_plain_term(doc, dataset)
            else:
                raise ValueError("Invalid data type to be indexed: %s" \
                        % str(type(data)))
        self._add_document_to_index(doc)

    def _create_empty_document(self):
        """create an empty document to be filled and added to the index later

        @return: the new document object
        @rtype: xapian.Document | PyLucene.Document
        """
        raise NotImplementedError("Incomplete indexer implementation: " \
                + "'_create_empty_document' is missing")
    
    def _add_plain_term(self, document, term):
        """add a term to a document

        @param document: the document to be changed
        @type document: xapian.Document | PyLucene.Document
        @param term: a single term to be added
        @type term: str
        """
        raise NotImplementedError("Incomplete indexer implementation: " \
                + "'_add_plain_term' is missing")

    def _add_field_term(self, document, field, term):
        """add a field term to a document

        @param document: the document to be changed
        @type document: xapian.Document | PyLucene.Document
        @param field: name of the field
        @type field: str
        @param term: term to be associated to the field
        @type term: str
        """
        raise NotImplementedError("Incomplete indexer implementation: " \
                + "'_add_field_term' is missing")

    def _add_document_to_index(self, document):
        """add a prepared document to the index database

        @param document: the document to be added
        @type document: xapian.Document | PyLucene.Document
        """
        raise NotImplementedError("Incomplete indexer implementation: " \
                + "'_add_document_to_index' is missing")

    def begin_transaction(self):
        """begin a transaction

        You can group multiple modifications of a database as a transaction.
        This prevents time-consuming database flushing and helps, if you want
        that a changeset is committed either completely or not at all.
        No changes will be written to disk until 'commit_transaction'.
        'cancel_transaction' can be used to revert an ongoing transaction.

        Database types that do not support transactions may silently ignore it.
        """
        raise NotImplementedError("Incomplete indexer implementation: " \
                + "'begin_transaction' is missing")

    def cancel_transaction(self):
        """cancel an ongoing transaction

        See 'start_transaction' for details.
        """
        raise NotImplementedError("Incomplete indexer implementation: " \
                + "'cancel_transaction' is missing")

    def commit_transaction(self):
        """submit the currently ongoing transaction and write changes to disk

        See 'start_transaction' for details.
        """
        raise NotImplementedError("Incomplete indexer implementation: " \
                + "'commit_transaction' is missing")

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
        raise NotImplementedError("Incomplete indexer implementation: " \
                + "'delete_document_by_id' is missing")

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
        raise NotImplementedError("Incomplete indexer implementation: " \
                + "'search' is missing")

    def delete_doc(self, ident):
        """delete the documents returned by a query

        @param ident: [list of] document IDs | dict describing a query | query
        @type ident: int | list of tuples | dict | list of dicts |
            query (e.g. xapian.Query) | list of queries
        """
        # turn a doc-ID into a list of doc-IDs
        if isinstance(ident, list):
            # it is already a list
            ident_list = ident
        else:
            ident_list = [ident]
        if len(ident_list) == 0:
            # no matching items
            return 0
        if isinstance(ident_list[0], int):
            # create a list of IDs of all successfully removed documents
            success_delete = [match for match in ident_list
                    if self.delete_document_by_id(match)]
            return len(success_delete)
        if isinstance(ident_list[0], dict):
            # something like: { "msgid": "foobar" }
            # assemble all queries
            query = self.make_query([self.make_query(query_dict, True)
                    for query_dict in ident_list], True)
        elif isinstance(ident_list[0], object):
            # assume a query object (with 'AND')
            query = self.make_query(ident_list, True)
        else:
            # invalid element type in list (not necessarily caught in the 
            # lines above)
            raise TypeError("description of documents to-be-deleted is not " \
                    + "supported: list of %s" % type(ident_list[0]))
        # we successfully created a query - now iterate through the result
        # no documents deleted so far ...
        remove_list = []
        # delete all resulting documents step by step
        def add_docid_to_list(match):
            """collect every document ID"""
            remove_list.append(match["docid"])
        self._walk_matches(query, add_docid_to_list)
        return self.delete_doc(remove_list)

    def _walk_matches(self, query, function):
        """use this function if you want to do something with every single match
        of a query

        example: self._walk_matches(query, function_for_match)
            'function_for_match' expects only one argument: the matched object
        @param query: a query object of the real implementation
        """
        # execute the query
        enquire = self.get_query_result(query)
        # start with the first element
        start = 0
        # do the loop at least once
        size, avail = (0, 1)
        # how many results per 'get_matches'?
        steps = 2
        while start < avail:
            (size, avail, matches) = enquire.get_matches(start, steps)
            for match in matches:
                function(match)
            start += size

    def set_field_analyzers(self, field_analyzers):
        """set the analyzers for different fields of the database documents

        possible analyzers are:
            CommonDatabase.ANALYZER_EXACT (default)
                the field value must excactly match the query string
            CommonDatabase.ANALYZER_PARTIAL
                the field value must start with the query string

        @param field_analyzers: mapping of field names and analyzers
        @type field_analyzers: dict containing field names and analyzers
        @throws: TypeError for invalid values in 'field_analyzers'
        """
        for field, analyzer in field_analyzers.items():
            # check for invald input types
            if not isinstance(field, str):
                raise TypeError("field name must be a string")
            if not isinstance(analyzer, int):
                raise TypeError("the analyzer must be a whole number (int)")
            # map the analyzer to the field name
            self.field_analyzers[field] = analyzer

    def get_field_analyzers(self, fieldnames=None):
        """return the analyzer that was mapped to a specific field

        see 'set_field_analyzers' for details

        The default analyzer is CommonDatabase.ANALYZER_EXACT

        @param fieldnames: the analyzer of this field (or all/multiple fields)
            is requested; leave empty (or "None") to request all fields
        @type fieldnames: str | list of str | None
        @return: the analyzer of the field - e.g. CommonDatabase.ANALYZER_EXACT
            or a dict of field names and analyzers
        @rtype: int | dict
        """
        default = self.ANALYZER_EXACT
        # all field analyzers are requested
        if fieldnames is None:
            # return a copy
            return dict(self.field_analyzers)
        # one field is requested
        if isinstance(fieldnames, str):
            if self.field_analyzers.has_key(fieldnames):
                return self.field_analyzers[fieldnames]
            else:
                return default
        # a list of fields is requested
        if isinstance(fieldnames, list):
            result = {}
            for field in fieldnames:
                result[field] = self.get_field_analyzers(field)
            return result
        return default


class CommonEnquire(object):
    """an enquire object contains the information about the result of a request
    """

    def __init__(self, enquire):
        """intialization of a wrapper around enquires of different backends

        @param enquire: a previous enquire
        @type enquire: xapian.Enquire | pylucene-enquire
        """
        self.enquire = enquire

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
        raise NotImplementedError("Incomplete indexing implementation: " \
                + "'get_matches' for the 'Enquire' class is missing")

