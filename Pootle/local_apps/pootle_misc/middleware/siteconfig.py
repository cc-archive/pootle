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

from django.http import HttpResponse
from pootle_misc import siteconfig
from pootle_misc import dbinit

"""some unused http status code to mark the need to auto install"""

INSTALL_STATUS_CODE = 613
class SiteConfigMiddleware(object):
    """
    This middleware does two things, it reload djblet siteconfigs on
    every request to ensure they're uptodate. but also works as an
    early detection system for database errors.

    It might seem strange that the middleware does these two unrelated
    tasks, but since the only way to test the database is to run a
    query, it would be too wasteful to add another query per request
    when siteconfig already requires one.

    """
    def process_request(self, request):
        """load site config, return a dummy response if database seems uninitialized"""
        #FIXME: can't we find a more efficient method?
        try:
            siteconfig.load_site_config()
        except Exception, e:
            #HACKISH: since exceptions thrown by different databases
            # do not share the same class heirarchy (DBAPI2 sucks) we
            # have to check the class name instead (since python uses
            # duck typing I will call this
            # poking-the-duck-until-it-quacks-like-a-duck-test
            
            if e.__class__.__name__ in ['OperationalError', 'ProgrammingError']:
                # we can't build the database here cause caching
                # middleware won't allow progressive loading of
                # response so instead return an empty response marked
                # with special status code INSTALL_STATUS_CODE
                
                response = HttpResponse()
                response.status_code = INSTALL_STATUS_CODE
                response.exception = e
                return response
            
    def process_response(self, request, response):
        """ this should be the last response processor to run, detect
        dummy response with INSTALL_STATUS_CODE status code and start
        db install process"""
        
        if response.status_code == INSTALL_STATUS_CODE:
            return HttpResponse(dbinit.staggered_install(response.exception))
        else:
            return response
            
