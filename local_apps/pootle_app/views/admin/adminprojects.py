#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008 Zuza Software Foundation
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with translate; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from django.utils.translation import ugettext as _
from pootle_app.views.admin import util
from pootle_project.models import Project
from pootle_app.admin import MyProjectAdminForm

@util.user_is_admin
def view(request):
    model_args = {}
    model_args['title'] = _("Projects")
    model_args['formid'] = "projects"
    model_args['submitname'] = "changeprojects"
    link = '/projects/%s/admin.html'
    return util.edit(request, 'admin/admin_general_projects.html', Project, model_args, link,
              form=MyProjectAdminForm, exclude='description', can_delete=True)
