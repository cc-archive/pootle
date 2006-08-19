

def open_database(uri):
    """Open a translation database."""
    protocol, path = uri.split('://')
    if protocol == 'mem':
        from Pootle.storage.memory import Database
        return Database()
    elif protocol == 'pootle':
        from Pootle.storage.standard import Database
        return Database(path)
    else: # Assume SQLAlchemy-handled protocol
        from Pootle.storage.rdb import Database
        return Database(uri)
