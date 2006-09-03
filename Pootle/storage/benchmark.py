#!/usr/bin/python

import sys
import time
import os
sys.path.append('../..')

from Pootle.storage import open_database

DB_FILENAME = 'test.db'
ENTRIES = 500
JUNK_STORES = 5


def main():
    try:
        write_bench()
        read_bench()
        add_junk()
        read_bench()
    finally:
        try:
            os.unlink(DB_FILENAME)
        except OSError:
            pass

def write_bench():
    db = open_database('sqlite:///' + DB_FILENAME)
    module = db.root.modules.add('module')
    store = module.add('lt')

    timer = Timer()
    units = [store.makeunit([('unit %d' % i, 'vertimas %d' % i)])
             for i in range(ENTRIES)]
    timer.checkpoint('store.makeunit * %d' % ENTRIES)
    store.fill(units)
    timer.checkpoint('store.fill()')
    store.save()
    timer.checkpoint('store.save()')


def add_junk():
    db = open_database('sqlite:///' + DB_FILENAME)
    module = db.root['module']

    print 'Adding %dx%d units of junk' % (JUNK_STORES, ENTRIES)
    timer = Timer()
    for lang in range(JUNK_STORES):
        print lang+1,
        sys.stdout.flush()
        store = module.add(str(lang))
        units = [store.makeunit([('unit %d' % i, 'abc %d' % i)])
                 for i in range(ENTRIES)]
        store.fill(units)
        store.save()
    print 
    timer.checkpoint('%d stores of junk' % JUNK_STORES)


def read_bench():
    for expr in ['store[%d]' % (ENTRIES // 2),
                 'list(store)',
                 'store.find("it")',
                 'store.find("it", limit=10)',
                 'store.find("it", search_target=False)',
                 'store.find("unit*", search_target=False, exact=True)',
                 'store.find("no match")',
                 'store.find("%d")' % (ENTRIES - 1),
                 ]:
        db = open_database('sqlite:///' + DB_FILENAME)
        store = db.root['module']['lt']

        timer = Timer()
        exec expr
        timer.checkpoint(expr)


class Timer(object):
    def __init__(self):
        self.last = time.time()

    def checkpoint(self, msg):
        print msg, ':  %.03f s' % (time.time() - self.last)
        self.last = time.time()


if __name__ == '__main__':
    main()
