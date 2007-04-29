#!/usr/bin/python

from SimpleAsyncHTTPServer import Server,RequestHandler
import asyncore, cgi, re

pofile_re = re.compile('(?P<dir>[\w/]+)/(?P<file>\w+\.po)?')

class PootleHandler(RequestHandler):
    
    def do_GET(self):
        print 'my get'
        qspos = self.path.find('?')
        if qspos >= 0:
            self.body = cgi.parse_qs(self.path[qspos+1:], keep_blank_values=1)
            self.path = self.path[:qspos]
        match = pofile_re.match(self.path)
        if match:
            print match.groupdict()
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

a = Server('',8000, PootleHandler)
# os.chdir('/home/hruske') # storage root
asyncore.loop()

