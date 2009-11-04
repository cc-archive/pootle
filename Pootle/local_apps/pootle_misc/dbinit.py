#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008-2009 Zuza Software Foundation
#
# This file is part of Pootle.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import sys

from django.core.management import call_command
from django.core.exceptions import ObjectDoesNotExist

from pootle.i18n.gettext import ugettext as _

from pootle_app.models import PootleProfile, Language, Project

def header(exception):
    text = """
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE html  PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html><head>
    <title>%(title)s</title>
    <meta content="text/html; charset=utf-8" http-equiv="content-type" />
    </head>
    <body>
    <h1>%(title)s</h1>
    <p>%(msg)s</p>
    """ % {'title': _('Pootle: Install'),
           'msg': _('Error: "%s" while attempting to access the Pootle database, will try to initialize database.', exception)}
    return text

def syncdb():
    text = u"""
    <p>%s</p>
    """ % _('Creating database tables...')
    call_command('syncdb', interactive=False)
    return text

def initdb():
    text = u"""
    <p>%s</p>
    """ % _('Creating default languages, projects and admin user')
    call_command('initdb')
    return text

def stats_start():
    text = u"""
    <p>%s
    <ul>
    """ % _('Calculating translation statistics, this will take a few minutes')
    return text

def stats_language(language):
    text = u"""
    <li>%s</li>
    """ % _('%(language)s is %(percent)d%% complete',
            {'language': language.localname(), 'percent': language.translated_percentage()})
    return text

def stats_project(project):
    text = u"""
    <li>%s</li>
    """ % _('Project %(project)s is %(percent)d%% complete',
            {'project': project.fullname, 'percent': project.translated_percentage()})
    return text

def stats_end():
    text = u"""
    </ul>
    %s</p>
    """ % _('Done calculating statistics for default languages and projects')
    return text
    
    
def footer():
    text = """
    <p>%(endmsg)s</p>
    <div><script>setTimeout("location.reload()", 10000)</script></div>
    </body></html>
    """  % { 'endmsg': _('Initialized database, you will be redirected to the fron page in 10 seconds') }
    return text

def staggered_install(exception):
    """Initialize the pootle database without displaying progress
    reports for each step"""

    # django's syncdb command prints progress repots to stdout, but
    # mod_wsgi doesn't like stdout, so we reroute to stderr
    stdout = sys.stdout
    sys.stdout = sys.stderr

    yield header(exception)

    # try to build the database tables
    yield syncdb()

    # having the correct database tables isn't enough for
    # pootle, it depends on the nobody (ie anonymous) user
    # having a profile.
    #
    # if the profile doesn't exist populate database with initial data
    try:
        PootleProfile.objects.get(user__username='nobody')
    except ObjectDoesNotExist:
        yield initdb()

    # first time to visit the front page all stats for projects and
    # languages will be calculated which can take forever, since users
    # don't like webpages that take forever let's precalculate the
    # stats here
    yield stats_start()
    for language in Language.objects.all():
        yield stats_language(language)
    for project in Project.objects.all():
        yield stats_project(project)
    yield stats_end()

    yield footer()

    # bring back stdout
    sys.stdout = stdout
    return