# This file is supposed to have all translation accessing functions in Pootle,
# at least the web portal part of it.

from urllib2 import urlopen
from urllib import urlencode
from Pootle.settings import STORAGE_ROOT_URL
from translate.storage.po import pounit

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

