
__author__ = "Gasper Zejn"

"""Implementation of a filesystem tags using extended file system attributes
It can use both python-pyxattr and python-xattr.

It provides functions get_tag, set_tag and del_tag, but most useful is 
create_tag, which returns tuple of above three functions.
"""

class XattrRequiredException(Exception): pass

try:
    import xattr
except ImportError:
    raise XattrRequiredException("xattr support is required for Pootle")

# xattr
def xattr_settag(filename, tagname, value):
    xattr.setxattr(filename, "user.%s" % str(tagname), str(value))

def xattr_gettag(filename, tagname):
    try:
        return xattr.getxattr(filename,"user.%s" % str(tagname))
    except IOError:
        return None

def xattr_deltag(filename, tagname):
    xattr.removexattr(filename, "user.%s" % str(tagname))

# choose the right implementation
set_tag, get_tag, del_tag = xattr_settag, xattr_gettag, xattr_deltag


# tag factory, particularly useful for properties
def create_tag(tagname):
    """Accepts a tag name and returns three functions suitable for 
    "property", eg: 

    >>> tag = property(*create_tag("mytagname"))
    """
    def _get_tag(self):
        return get_tag(self, tagname)

    def _set_tag(self, value):
        set_tag(self, tagname, value)

    def _del_tag(self):
        del_tag(self, tagname)

    return _get_tag, _set_tag, _del_tag

