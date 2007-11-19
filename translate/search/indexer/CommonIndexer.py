"""
base class for interfaces to indexing engines for pootle
"""

__revision__ = "$Id$"


class CommonDatabase(object):
    """base class for indexing support

    any real implementation must override most methods of this class
    """

    """mapping of field names and analyzers - see 'set_field_analyzers'"""
    field_analyzers = {}

    """exact matching: the query string must equal the whole term string"""
    ANALYZER_EXACT = 0
    """partial matching: a document matches, even if the query string only
    matches the beginning of the term value"""
    ANALYZER_PARTIAL = 1

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
        # do nothing - the derived class should do everything
        pass

    def flush(self, optimize=False):
        """flush the content of the database - to force changes to be written
        to disk

        some databases also support index optmization

        @param optimize: should the index be optimized if possible?
        @type optimize: bool
        """
        raise NotImplementedError("Incomplete indexer implementation: " \
                + "'flush' is missing")

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

    def index_data(self, data):
        """add the given data to the database

        @param data: the data to be indexed
        @type data: dict | list of tuples
        """
        raise NotImplementedError("Incomplete indexer implementation: " \
                + "'index_data' is missing")

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
        @type fieldnames: string | list of strings | tuple of strings
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

    def get_field_analyzer(self, fieldname):
        """return the analyzer that was mapped to a specific field

        see 'set_field_analyzers' for details

        The default analyzer is CommonDatabase.ANALYZER_EXACT

        @param fieldname: the analyzer of this field is requested
        @type fieldname: str
        @return: the analyzer of the field - e.g. CommonDatabase.ANALYZER_EXACT
        @rtype: int
        """
        try:
            return self.field_analyzers[fieldname]
        except KeyError:
            return self.ANALYZER_EXACT


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

