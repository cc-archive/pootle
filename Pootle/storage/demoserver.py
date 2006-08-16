#!/usr/bin/python
"""A proof of concept XML-RPC server that exposes Pootle's backend storage.

After starting the server you can use it like this:

    from xmlrpclib import ServerProxy
    server = ServerProxy('http://localhost:23123')
    server.translate('pootle', 'lt', '', 'pootle', 'Project')

"""

import sys
import os
from SimpleXMLRPCServer import SimpleXMLRPCServer

sys.path.append('../..')

from Pootle.storage.standard import Database
from Pootle.storage.po import read_po

STORAGE_ROOT = '../po'


def translate(project, lang, country, module, msgid):
    """Translate a given msgid.

    You may pass '' instead of None as the country code.
    """
    db = Database(STORAGE_ROOT)
    if not country: # avoid trouble with passing None as an argument
        country is None
    store = db.root[project][module][lang, country]
    return store.translate(msgid)


def main():
    server = SimpleXMLRPCServer(('localhost', 12123))
    server.register_function(translate)
    server.serve_forever()


if __name__ == '__main__':
    main()
