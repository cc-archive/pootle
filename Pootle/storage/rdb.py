"""A backend that stores all data in a relational database.

Requires sqlalchemy.
"""

from Pootle.storage.api import IDatabase
import sqlalchemy

DEBUG_ECHO = False # set to True to echo SQL statements


class Folder(object):
#    _interface = IFolder

    # TODO: use ORM

    def __init__(self, key, parent):
        self.key = key
        self.parent = parent


class Database(Folder):
    """An SQL database connection."""
#    _interface = IDatabase

    def __init__(self, engine_url):
        """Create a new connection.

        `engine_url` is an engine identifier, e.g.:
            'sqlite://' (in-memory database)
            'sqlite:////absolute/path/to/database.txt'
            'sqlite:///relative/path/to/database.txt'
            'postgres://scott:tiger@localhost:5432/mydatabase'
            'mysql://localhost/foo'
        """
        # TODO: connection pooling
        self.engine = sqlalchemy.create_engine(engine_url, echo=DEBUG_ECHO)
        self.create_tables() # TODO Don't recreate tables every time.

    def create_tables(self):
        metadata = sqlalchemy.MetaData()
        folders = sqlalchemy.Table('folders', metadata,
            sqlalchemy.Column('folder_id', sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column('key', sqlalchemy.String(100), nullable=False),
            sqlalchemy.Column('parent', sqlalchemy.Integer, nullable=False))
        # TODO: other objects

        metadata.create_all(engine=self.engine)
