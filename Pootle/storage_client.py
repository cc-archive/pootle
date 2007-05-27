# This file is supposed to have all translation accessing functions in Pootle,
# at least the web portal part of it.

from urllib2 import urlopen
from urllib import urlencode
from Pootle.settings import STORAGE_ROOT_URL
from translate.storage.po import pounit
import re

list_remote_re = re.compile("([\w\./]+?)? stats t: (\d+)w (\d+)s (\d+)p f: (\d+)w (\d+)s (\d+)p u: (\d+)w (\d+)s (\d+)p all: (\d+)w (\d+)s\n")

class ImproperlyConfigured(Exception): pass


class StorageFile(object):
    
    def __init__(self, content):
        self.stats = content[1]
        self.val = content[0]
        if self.val.endswith("/"): # is a dir
            self.icon = 'folder'
            self.href = '%s' % self.val
            self.isdir = True
            self.isfile = False
        else: # is a file
            self.icon = 'file'
            self.href = '%s' % self.val
            self.isdir = False
            self.isfile = True
    
    def basename(self):
        return str(self.val)
            

_layout = None
def get_layout():
    global _layout
    if not _layout:
        # FIXME: Not nice
        url = storage_root + 'storage-status'
        opened_url = urlopen(url)
        data = opened_url.read()
        opened_url.close()
        data = data.split("<br />")
        info = dict([ line.split("=") for line in data])
        set_layout(**info)
    return _layout

def set_layout(storage_layout):
    global _layout
    _layout = storage_layout
    return _layout

def get_po_dir(translation_project):
    if get_layout() == 'translator':
        return "/%s/%s/" % (translation_project.language.code, translation_project.project.code)
    elif get_layout() == 'provider':
        return "/%s/%s/" % (translation_project.project.code, translation_project.language.code)

if STORAGE_ROOT_URL.endswith("/"):
    storage_root = STORAGE_ROOT_URL
else:
    storage_root = STORAGE_ROOT_URL + '/' 

def get_unit(file, id, unit=None):
    """Fetch unit from storage server.
    file is path to file on server, id is unit id in file (header has id=1) and
    optional parameter unit serves for commiting changes back"""
    url = "%s%s/%s" % (storage_root, file, str(id))

    if unit:
        send_data = urlencode( {'translation': str(unit)} )
    else:
        send_data = None
    a = urlopen(url, send_data)
    recv_data = a.read()
    info = a.info()
    fetched_unit = pounit()
    fetched_unit.parse(recv_data)
    return fetched_unit, info

def post_unit(file, id, unit):
    return get_unit(file, id, unit)


def listdir(dirname):
    if dirname.startswith("/"):
        url = storage_root + dirname[1:]
    else:
        url = storage_root + dirname
    
    urlfd = urlopen(url)
    data = urlfd.read()
    urlfd.close()

    dirlist = []
    cur = 0
    match = list_remote_re.match(data, cur)
    while match:
        direntry = match.groups()
        dirlist.append( StorageFile((direntry[0], map(int, direntry[1:]))))
        cur = match.end()
        match = list_remote_re.match(data, cur)
    return dirlist


