"""
interface for the pylucene (v1.x) indexing engine

take a look at PyLuceneIndexer.py for PyLucene v2.x support
"""

__revision__ = "$Id$"

# this module is based on PyLuceneIndexer (for PyLucene v2.x)
import PyLuceneIndexer
import PyLucene


def is_available():
    return PyLuceneIndexer._get_pylucene_version() == 1


class PyLuceneDatabase(PyLuceneIndexer.PyLuceneDatabase):
    """manage and use a pylucene indexing database"""

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
        qp = PyLucene.QueryParser()
        if require_all:
            qp.setDefaultOperator(qp.Operator.AND)
        else:
            qp.setDefaultOperator(qp.Operator.OR)
        if analyzer == self.ANALYZER_EXACT:
            pass
        elif analyzer == self.ANALYZER_PARTIAL:
            # PyLucene uses explicit wildcards for partial matching
            text += "*"
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
        return PyLucene.QueryParser.parse(value, field)

    def _create_query_combined(self, queries, require_all=True):
        """generate a combined query

        @param queries: list of the original queries
        @type queries: list of xapian.Query
        @param require_all: boolean operator
            (True -> AND (default) / False -> OR)
        @type require_all: bool
        @return: the resulting combined query object
        @rtype: PyLucene.Query
        """
        combined_query = PyLucene.BooleanQuery()
        for query in queries:
            combined_query.add(
                    PyLucene.BooleanClause(query, require_all, False))
        return combined_query

    def _add_plain_term(self, document, term):
        """add a term to a document

        @param document: the document to be changed
        @type document: xapian.Document | PyLucene.Document
        @param term: a single term to be added
        @type term: str
        """
        document.add(PyLucene.Field(str(PyLuceneIndex.UNNAMED_FIELD_NAME), term,
                True, True, True))

    def _add_field_term(self, document, field, term):
        """add a field term to a document

        @param document: the document to be changed
        @type document: xapian.Document | PyLucene.Document
        @param field: name of the field
        @type field: str
        @param term: term to be associated to the field
        @type term: str
        """
        # TODO: decoding (utf-8) is missing
        document.add(PyLucene.Field(str(field), str(term), True, True, True))

    def get_query_result(self, query):
        """return an object containing the results of a query
        
        @param query: a pre-compiled query
        @type query: a query object of the real implementation
        @return: an object that allows access to the results
        @rtype: subclass of CommonEnquire
        """
        return PyLucene.indexSearcher.search(query)

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
        hits = PyLucene.indexSearcher.search(query)
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
        super(PyLuceneIndexer1, self).__init__()
        self.writer.maxFieldLength = PyLuceneIndexer.MAX_FIELD_SIZE

