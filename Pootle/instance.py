"""
This file is a bridge to enable some features, that were previously enabled by 
jToolkit provided server. These include:
 - instance, a python code representation of 'pootle.prefs' file 
 - potree, the global object through which translations are accessed
 - users, the python representation of 'users.prefs' user database

Since these objects were previously instantiated in a way specific to 
jToolkit server, this code acts as a bridge between these differences.
"""

from django.conf import settings
from Pootle import potree
from Pootle.conf import set_instance
from jToolkit import prefs
import os

serverprefs = prefs.PrefsParser()
serverprefs.parsefile(settings.POOTLE_PREFS)
instance = serverprefs
# find the instance prefs
try:
    instance = serverprefs
    if settings.POOTLE_INSTANCE:
        for part in settings.POOTLE_INSTANCE.split("."):
            instance = getattr(instance, part)
except AttributeError:
    errormessage = "Prefs file %r has no attribute %r\nprefs file is %r, attributes are %r" \
                   % (settings.POOTLE_PREFS, settings.POOTLE_INSTANCE, serverprefs, [top[0] for top in serverprefs.iteritems()])
    raise AttributeError(errormessage)


users = prefs.PrefsParser()
users.parsefile(os.path.join(os.path.dirname(settings.POOTLE_PREFS), instance.userprefs))

# set instance and potree globally
set_instance(instance, potree.POTree(instance), users)
