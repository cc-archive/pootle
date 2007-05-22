#!/usr/bin/python

from SimpleAsyncHTTPServer import Server,RequestHandler
import asyncore, cgi, re, urllib, os
from Pootle.storage.storagelayout import gettext_path
from Pootle.path import path
from urllib import quote
from Pootle.storage import settings

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

pounit_re = re.compile(r'^/(?P<directory>[\w/]+)/(?P<filename>\w+.po)/(?P<id>\d+)/?$')
pofile_re = re.compile(r'^/(?P<directory>[\w/]+)/(?P<filename>\w+.po)/?$')
podir_re = re.compile(r'^/(?P<directory>[\w/]+)/$')
root_re = re.compile(r'^/$')

urlmaps = [
    (pounit_re, 'unit'),
    (pofile_re, 'file'),
    (podir_re, 'dir'),
    (root_re, 'root')
]

STORAGE_ROOT = None


class PootleHandler(RequestHandler):
    
    def gettext_path_or_404(self, file_path):
        a = gettext_path(file_path)
        if not a.exists():
            self.send_error(404, 'File not found')
            return 
        return a

    def serve_unit(self, directory, filename, id):
        a = self.gettext_path_or_404(STORAGE_ROOT / directory / filename)
        id = int(id)

        if self.POST:
            try:
                a[id] = self.body['translation'][0]
            except ValueError:
                # FIXME, parsing pounit didn't succeed
                print 'error'
            self.send_response(302)
            self.send_header("Location", quote(self.path))
            self.end_headers()
        else:
            self.send_response(200)
            self.send_header("Content-type", 'text/plain')
            self.send_header("Content-charset", 'utf-8')
        
            unit, stats = a[id]
            response = str(unit)
            self.send_header("Pootle-checks", str(stats))
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)
    
    def serve_file(self, directory, filename):
        a = self.gettext_path_or_404(STORAGE_ROOT / directory / filename)

        self.send_response(200)
        self.send_header("Content-type", 'text/plain')
        self.send_header("Content-charset", 'utf-8')
        self.send_header("Content-Length", str(a.current.size))
        self.end_headers()
        self.copyfile(a.current.open(), self.wfile)

    def serve_dir(self, directory):
        a = STORAGE_ROOT / directory 
        if not a.exists():
            self.send_error(404, "File not found")
            return None
        f = self.list_directory(str(a))
        response = f.getvalue()
        self.wfile.write(response)

    def serve_root(self):
        f = self.list_directory(STORAGE_ROOT)
        response = f.getvalue()
        self.wfile.write(response)

    def handle_data(self):
        for pattern, func in urlmaps:
            match = pattern.match(self.path)
            if match:
                if hasattr(self, 'serve_' + func):
                    return getattr(self, 'serve_'+func)(**match.groupdict())
        self.send_error(404, 'Path not found')
        return None
        
    def do_GET(self):
        self.body = {}
        self.POST = False
        self.handle_data()

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
        
        self.POST = True

        self.handle_data()

    def foo(self):
        a = gettext_path(STORAGE_ROOT / 'test' / 'test.po' )
        try:
            a[3] = self.body['translation'][0]
        except ValueError:
            # FIXME, parsing pounit didn't succeed
            print 'error'

        self.send_response(302)
        self.send_header("Location", quote(self.path))
        self.end_headers()

    def list_directory(self, path):
        """Taken from SimpleHTTPServer.py and adapted to output
        a more machine parsable format.
        """
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        f = StringIO()

        displaypath = cgi.escape(urllib.unquote(self.path))
        f.write("<title>Directory listing for %s</title>\n" % displaypath)

        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            f.write('<a href="%s">%s</a><br />'
                    % (urllib.quote(linkname), cgi.escape(displayname)))
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f


def set_storage_root(storage_root):
    global STORAGE_ROOT

    STORAGE_ROOT = path(storage_root)

def run_storage():
    if STORAGE_ROOT == None:
        raise ValueError('cannot run uninitialized; please call set_storage_root first')
    a = Server('',8080, PootleHandler)
    # os.chdir(STORAGE_ROOT) # storage root
    print 'Server listening'
    asyncore.loop()

def main():
    set_storage_root(settings.STORAGE_ROOT_PATH)
    run_storage()

if __name__ == "__main__":
    main()
