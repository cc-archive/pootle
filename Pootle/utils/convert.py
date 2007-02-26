
from cStringIO import StringIO
from Pootle.utils import NotImplementedException

po2csv = None
po2ts = None
po2xliff = None

def _po2csv(inputfile):
    global po2csv

    if po2csv == None:
        from translate.convert.po2csv import po2csv
    converter = po2csv()
    data = converter.convertfile(inputfile.translationstore)    
    return str(data)

def _po2po(inputfile):
    return inputfile.bytes()

def _po2ts(inputfile):
    global po2ts

    if po2ts == None:
        from translate.convert.po2ts import po2ts
    converter = po2ts()
    data = converter.convertfile(inputfile.translationstore)
    return str(data)

def _po2xliff(inputfile):
    global po2xliff
    
    if po2xliff == None:
        from translate.convert.po2xliff import po2xliff
    converter = po2xliff()
    data = converter.convertfile(inputfile.translationstore)
    return str(data)

_po_converters = {
    'csv': _po2csv,
    'po': _po2po,
    'ts': _po2ts,
    'xliff': _po2xliff,
    }

def convert_translation_store(inputpath, outputfd, format):
    """Convert between translation store formats. 
    inputpath -- path of current translation store (should be a 
                 Pootle.path.path object.
    outputfd -- an object with write method
    format -- target format to convert into
    """

    if inputpath.is_po_file():
        outputfd.write(str(_po_converters[format](inputpath)))
    raise NotImplementedException

