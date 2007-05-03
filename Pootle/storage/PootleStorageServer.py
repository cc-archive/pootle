#!/usr/bin/python

from SimpleAsyncHTTPServer import Server,RequestHandler
import asyncore, cgi, re
from Pootle.storage.storagelayout import gettext_path
from Pootle.path import path
from urllib import quote

pofile_re = re.compile(r'^/(?P<dir>[\w/]+)/((?P<file>\w+.po)(/(?P<id>\d+)/?)?)?$')
root_re = re.compile(r'^/$')

STORAGE_ROOT = None

class PootleHandler(RequestHandler):
    
    def do_GET(self):
        self.body = {}
        match = pofile_re.match(self.path)
        if match:
            mdict = match.groupdict()
            if mdict['file']:
                self.send_response(200)
                self.send_header("Content-type", 'text/plain')
                self.send_header("Content-charset", 'utf-8')
                a = gettext_path(STORAGE_ROOT / mdict['dir'] / mdict['file'])

                if a.exists():
                    if mdict['id']:
                        # return only one translation
                        id = int(mdict['id'])
                        response = str(a[id])
                        self.send_header("Content-Length", str(len(response)))
                        self.end_headers()
                        self.wfile.write(response)
                    else:
                        # send whole file
                        self.send_header("Content-Length", str(a.current.size))
                        self.end_headers()
                        self.copyfile(a.current.open(), self.wfile)
            else:
                # if no file, then list dir
                if not mdict['dir']:
                    return None

                a = STORAGE_ROOT / mdict['dir']
                if not a.exists():
                    self.send_error(404, "File not found")
                    return None
                f = self.list_directory(str(a))
                response = f.getvalue()
                self.wfile.write(response)
        else:
            match = root_re.match(self.path)
            if match:
                # list root dir
                f = self.list_directory(STORAGE_ROOT)
                response = f.getvalue()
                self.wfile.write(response)
            else:
                self.send_error(404, 'File not found')
                return None

    def handle_data(self):
        pass
        
    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        length = int(self.headers.getheader('content-length'))
        
        if ctype == 'multipart/form-data':
            self.body = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            qs = self.rfile.read(length)
            self.body = cgi.parse_qs(qs, keep_blank_values=1)
        else:
            self.body = '' # unknown content type
        
        a = gettext_path(STORAGE_ROOT / 'test' / 'test.po' )
        try:
            a[3] = self.body['translation'][0]
        except ValueError:
            # FIXME, parsing pounit didn't succeed
            print 'error'

        self.send_response(302)
        self.send_header("Location", quote(self.path))
        self.end_headers()

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
