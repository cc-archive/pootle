# this is here to make sure Django Pootle sets up global variables
import Pootle.instance

from django.conf.urls.defaults import *

urlpatterns = patterns('Pootle.web.views',
    (r'^$', 'index'),
    (r'^login.html$', 'login'),
    (r'^register.html$', 'register'),
    (r'^activate.html$', 'activate'),
    (r'^about/$', 'about'),
    (r'^options/$', 'options'),
    (r'^(?P<what>languages)/$', 'index'),
    
    (r'^(?P<what>projects)/$', 'index'),
    (r'^projects/(?P<project>\w+)/$', 'project'),
    (r'^projects/(?P<project>\w+)/index.html$', 'project'),
    (r'^projects/(?P<project>\w+)/admin.html$', 'projectadmin'),
    
    (r'^admin/$', 'admin'),
    (r'^admin/index.html$', 'admin'),
    (r'^admin/users/$', 'admin_users'),
    (r'^admin/users/(?P<user>\w+)/$', 'admin_useredit'),
    (r'^admin/languages/$', 'admin_languages'),
    (r'^admin/projects/$', 'admin_projects'),
    (r'^admin/projects/(?P<project>\w+)/$', 'admin_projectedit'),

    
    (r'^(?P<language>\w+)/$', 'language'),
    (r'^(?P<language>\w+)/(?P<project>\w+)/$', 'translationproject'),
    (r'^(?P<language>\w+)/(?P<project>\w+)/browse/(?P<subdir>[\w/]*?)$', 'translationproject'),
    (r'^(?P<language>\w+)/(?P<project>\w+)/translate/(?P<subdir>[\w/]*?)(?P<filename>\w+)\.po', 'translatepage'),
    (r'^(?P<language>\w+)/(?P<project>\w+)/download/(?P<subdir>[\w/]*?)(?P<filename>\w+)\.po', 'downloadfile'),
    (r'^(?P<language>\w+)/(?P<project>\w+)/review/(?P<subdir>[\w/]*?)(?P<filename>\w+)\.po', 'review'),
    
    (r'^(?P<language>\w+)/(?P<project>\w+)/admin/', 'admintranslationproject'),
    (r'^(?P<language>\w+)/(?P<project>\w+)/(.*)/spellcheck.html$', 'spellcheck'),
    (r'^(?P<language>\w+)/(?P<project>\w+)/(.*)/spellingstandby.html$', 'spellingstandby'),


    (r'^robots.txt$', 'robots'),
)
