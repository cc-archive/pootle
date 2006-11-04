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


# set instance and potree globally
set_instance(instance, potree.POTree(instance))


users = prefs.PrefsParser()
users.parsefile(os.path.join(os.path.dirname(settings.POOTLE_PREFS), instance.userprefs))
