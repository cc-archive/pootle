# this is here to make sure Django Pootle sets up global variables
import Pootle.instance

from django.conf.urls.defaults import *
from django.conf import settings


if settings.DEBUG:
    urlpatterns = patterns('',
        (r'^test/$', 'Pootle.web.views.test'),
        # js, images, pootle.css, /favicon.ico
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT} ),
    )
else:
    urlpatterns = patterns('', )

if settings.POOTLE_BACKWARDS_COMPATIBILITY:
    urlpatterns += patterns('',
        (r'^', include('Pootle.compat.urls')),
    )
else:
    urlpatterns += patterns('',
        (r'^', include('Pootle.web.urls')),
    )

