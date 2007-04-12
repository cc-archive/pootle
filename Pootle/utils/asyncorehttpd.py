import asyncore
import logging
import socket
import time
import mimetools
import os
import sys
from errno import EWOULDBLOCK
from datetime import datetime

from BaseHTTPServer import DEFAULT_ERROR_MESSAGE, _quote_html, BaseHTTPRequestHandler

__version__ = "0.2"

 

class BreakoutError(Exception): pass

class readline_wrapper:
    """a mimetools.Message compatibility wrapper

    it is sufficient to provide a readline interface"""
    def __init__(self, line_list):
        self.lines = line_list
    def readline(self):
        if len(self.lines) > 0:
            return self.lines.pop(0)
        return ''

class AsyncoreHTTPServer(asyncore.dispatcher):
    server_version = "AsyncoreHTTPServer/" + __version__
    def __init__(self, localaddr):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(localaddr)
        self.listen(5)
        self.log_output = sys.stderr
        self.log("Server listening.")

    def handle_accept(self):
        conn, addr = self.socket.accept()
        channel = HTTPChannel(self, conn, addr)
    
    def readable(self):
        return True

    def writable(self):
        return False

class HTTPChannel(asyncore.dispatcher):

    MessageClass = mimetools.Message
    protocol_version = "HTTP/1.0"
    responses = BaseHTTPRequestHandler.responses
    sys_version = 'Python/' + sys.version.split()[0]

    def __init__(self, server, conn, addr):
        asyncore.dispatcher.__init__(self)
        self.__server = server
        self.__conn = conn
        self.__addr = addr
        self.__in_buffer = ''
        self.__in_buffer_size = 4096
        self.__out_buffer_size = 4096
        self.response_code = 200
        self.__out_buffer = ''
        self.command = None
        self.headers = None
        self.__headers = []
        self.__request_version = None
        self.__headers_finished = False
        self.first_line = None
        self.__out_headers = {}
        self.content = None
        self.set_socket(conn)
        self.socket.setblocking(0)

    def handle_write(self):
        
        self.log_info('write')
        self.send("Content-type: text/html\r\n\r\nhelo\r\n")
        self.close()

    def writable(self):
        return self.__headers_finished and self.content
    
    def readable(self):
        return not self.__headers_finished

    def close(self):
        self.log()
        asyncore.dispatcher.close(self)

    def log(self, user=None):
        # FIXME: user, response code, length
        self.__server.log_output.write('%s - %s %s "%s" %s\n' % (
            self.__addr[0], 
            user or '-', 
            datetime.now().strftime("[%d/%h/%Y %H:%M:%S]"), 
            self.__firstline,
            self.response_code))

    def log_info(self, msg, type='info'):
        print "LOG: " + msg

    def handle_read(self):
        try:
            data = self.recv(self.__in_buffer_size)
        except socket.error, why:
            if why[0] == EWOULDBLOCK: # fix asyncore.py ?
                return  
            self.handle_error()
            return 
        
        self.__in_buffer += data
        try:
            while not self.__headers_finished:
                try:
                    eol = self.__in_buffer.index('\n') 
                except ValueError:
                    raise BreakoutError
                requestline = self.__in_buffer[:eol]
                self.__headers.append(self.__in_buffer[:eol+1]) 
                self.__in_buffer = self.__in_buffer[eol+1:]

                if requestline[-1] == '\r':
                    requestline = requestline[:-1]
                if self.command == None:
                    self.__firstline = requestline
                    self.__headers.pop(0)
                    self.close_connection = 1
                    self.request_version = version = "HTTP/0.9"
                    words = requestline.split()
                    if len(words) == 3:
                        [command, path, version] = words
                        if version[:5] != 'HTTP/':
                            self.send_error(400, "Bad request version (%s)" % version)
                            return False
                        try:
                            base_version_number = version.split('/', 1)[1]
                            version_number = base_version_number.split('.')
                            if len(version_number) != 2:
                                raise ValueError
                            version_number = int(version_number[0]), int(version_number[1])
                        except (ValueError, IndexError):
                            self.send_error(400, "Bad request version (%r)" % version)
                            return False
                        if version_number >= (1,1) and self.protocol_version >= "HTTP/1.1":
                            self.close_connection = 0
                        if version_number >= (2,0):
                            self.send_error(505, "Invalid HTTP Version (%s)" % base_version_number)
                            return False
                    elif len(words) == 2:
                        [command, path] = words
                        self.close_connection = 1
                        if command != 'GET':
                            self.send_error(400, "Bad HTTP/0.9 request type(%r)" % command)
                            return False
                    elif not words:
                        return False
                    else:
                        self.send_error(400, "Bad request syntax (%r)" % requestline)
                        return False
                    self.command, self.path, self.request_version = command, path, version

        except BreakoutError:
            self.__headers_finished = True

        if self.__headers_finished:
            self.headers = mimetools.Message(readline_wrapper(self.__headers),0)
        self.handle()
    
    def handle(self):
        "Handler for a single request"
        mname = 'do_' + self.command
        if not hasattr(self, mname):
            self.send_error(501, "Unsupported method (%r)" % self.command)
            return 
        method = getattr(self, mname)
        method()
        
    def do_GET(self):
        self.content = 'Hello world!\r\nAnd you too.'        
        self.response_code = 200

    def send_error(self, code, message=None):
        "Sends an error page to client."
        try:
            short, long = self.responses[code]
        except KeyError:
            short, long = '???', '???'
        if message is None:
            message = short

        explain = long
        self.response_code = code
        if self.command != 'HEAD' and code >= 200 and code not in (204, 304):
            self.content = (DEFAULT_ERROR_MESSAGE % { 
                            'code': code,
                            'message': _quote_html(message),
                            'explain': explain, })
        else:
            self.content = None
        self.add_header('Content-Type', 'text/html')
        self.add_header('Connection', 'close')
        self.send_response()
        
    def add_header(self, keyword, value):
        self.__out_headers[keyword] = value
    
    def date_time_string(self):
        """Return the current date and time formatted for a message header."""
        now = time.time()
        year, month, day, hh, mm, ss, wd, y, z = time.gmtime(now)
        s = "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
                self.weekdayname[wd],
                day, self.monthname[month], year,
                hh, mm, ss)
        return s
            
    def version_string(self):
        return self.__server.server_version + ' ' + self.sys_version

    def send_response(self):
        self.add_header('Server', self.version_string())
        self.add_header('Date', self.date_time_string())

        if self.request_version != 'HTTP/0.9':
            self.__out_buffer = "\r\n".join(["%s: %s" % (i,i) for i in self.__out_headers.iteritems()]) + "\r\n"

if __name__ == "__main__":
    HOST = '127.0.0.1'
    PORT = 9999
    a = AsyncoreHTTPServer((HOST,PORT))
    asyncore.loop()
    
    
    
