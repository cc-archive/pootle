# This file is supposed to have all translation accessing functions in Pootle,
# at least the web portal part of it.

from urllib2 import urlopen
from Pootle.settings import STORAGE_ROOT_URL
from translate.storage.po import pounit

if STORAGE_ROOT_URL.endswith("/"):
    storage_root = STORAGE_ROOT_URL
else:
    storage_root = STORAGE_ROOT_URL + '/' 

def get_unit(file, id):
    url = "%s%s/%d" % (storage_root, file, id)
    a = urlopen(url)
    data = a.read()
    unit = pounit()
    unit.parse(data)
    return unit

