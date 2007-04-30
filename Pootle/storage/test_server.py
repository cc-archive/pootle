#!/usr/bin/python

from SimpleAsyncHTTPServer import Server,RequestHandler
import asyncore, cgi, re
from Pootle.storage.dirlayout import gettext_path
from Pootle.path import path

pofile_re = re.compile(r'/(?P<dir>[\w/]+)/((?P<file>\w+.po)(/(?P<id>\d+)/)?)?')

STORAGE_ROOT = None

class PootleHandler(RequestHandler):
    
    def do_GET(self):
        print 'my get'
        qspos = self.path.find('?')
        if qspos >= 0:
            self.body = cgi.parse_qs(self.path[qspos+1:], keep_blank_values=1)
            self.path = self.path[:qspos]
        match = pofile_re.match(self.path)
        if match:
            mdict = match.groupdict()
            if mdict['file']:
                a = gettext_path(STORAGE_ROOT / mdict['dir'] / mdict['file'])

                if a.exists():
                    if mdict['id']:
                        # return only one translation
                        id = int(mdict['id'])
                        print a[id]

            else:
                print 'file not present'
            print mdict
        self.handle_data()

        
        
    def do_POST(self):
        print 'my post'
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        length = int(self.headers.getheader('content-length'))
        if ctype == 'multipart/form-data':
            self.body = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            qs = self.rfile.read(length)
            self.body = cgi.parse_qs(qs, keep_blank_values=1)
        else:
            self.body = '' # unknown content type
        self.handle_data()


def set_storage_root(storage_root):
    global STORAGE_ROOT

    STORAGE_ROOT = storage_root

def run_storage():
    if STORAGE_ROOT == None:
        raise ValueError('cannot run uninitialized; please call set_storage_root first')
    a = Server('',8000, PootleHandler)
    # os.chdir(STORAGE_ROOT) # storage root
    print 'Server listening'
    asyncore.loop()

if __name__ == "__main__":
    set_storage_root(path('/home/hruske/projekti/pootle/django-migration/Pootle/storage/testroot/'))
    run_storage()
