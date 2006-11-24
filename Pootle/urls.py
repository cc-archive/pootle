# this is here to make sure Django Pootle sets up global variables
import Pootle.instance

from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    # js, images, pootle.css, /favicon.ico
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT} ),
)

urlpatterns += patterns('Pootle.web.views',
    (r'^$', 'index'),
    (r'^login.html$', 'login'),
    (r'^register.html$', 'register'),
    (r'^activate.html$', 'activate'),
    (r'^about.html$', 'about'),
    (r'^home/$', 'home'),
    (r'^home/index.html$', 'home'),
    (r'^home/options.html$', 'options'),
    (r'^(?P<what>languages)/$', 'index'),
    
    (r'^(?P<what>projects)/$', 'index'),
    (r'^projects/(?P<project>\w+)/$', 'projectlanguageindex'),
    (r'^projects/(?P<project>\w+)/index.html$', 'projectlanguageindex'),
    (r'^projects/(?P<project>\w+)/admin.html$', 'projectadmin'),
    
    (r'^admin/$', 'admin'),
    (r'^admin/index.html$', 'admin'),
    (r'^admin/users.html$', 'adminusers'),
    (r'^admin/languages.html$', 'adminlanguages'),
    (r'^admin/projects.html$', 'adminprojects'),
    
    (r'^(?P<language>\w+)/$', 'languageindex'),
    (r'^(?P<language>\w+)/(?P<project>\w+)/$', 'projectindex'),
    (r'^(?P<language>\w+)/(?P<project>\w+)/index.html$', 'projectindex'),
    
    (r'^(?P<language>\w+)/(?P<project>\w+)/admin.html', 'admintranslationproject'),
    (r'^(?P<language>\w+)/(?P<project>\w+)/translate.html$', 'translatepage'),
    (r'^(?P<language>\w+)/(?P<project>\w+)/(.*)/(.*).po?translate$', 'translatepage'),
    (r'^(?P<language>\w+)/(?P<project>\w+)/(.*)/spellcheck.html$', 'spellcheck'),
    (r'^(?P<language>\w+)/(?P<project>\w+)/(.*)/spellingstandby.html$', 'spellingstandby'),


    (r'^robots.txt$', 'robots'),
)
