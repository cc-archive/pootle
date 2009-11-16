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

import locale

from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext

from pootle_app.models              import Project, Suggestion, Submission
from pootle_app.views.language.project_index import get_stats_headings
from pootle_app.views.language.item_dict import add_percentages, stats_descriptions
from pootle.i18n.gettext import tr_lang
from pootle_app.views.top_stats import gentopstats
from pootle_app.views import pagelayout


def limit(query):
    return query[:5]

def make_language_item(request, translation_project):
    href = '/%s/%s/' % (translation_project.language.code, translation_project.project.code)
    projectstats = add_percentages(translation_project.getquickstats())
    info = {
        'code': translation_project.language.code,
        'href': href,
        'title': tr_lang(translation_project.language.fullname),
        'data': projectstats,
    }
    info.update(stats_descriptions(projectstats))
    return info


def view(request, project_code, _path_var):
    project = get_object_or_404(Project, code=project_code)
    translation_projects = project.translationproject_set.all()
    items = [make_language_item(request, translation_project) for translation_project in translation_projects]
    items.sort(lambda x, y: locale.strcoll(x['title'], y['title']))
    languagecount = len(translation_projects)
    totals = add_percentages(project.getquickstats())
    average = totals['translatedpercentage'] 

    topstats = gentopstats(lambda query: query.filter(translation_project__project__code=project_code))

    templatevars = {
        'project': {
          'code': project.code,
          'name': project.fullname,
          'stats': ungettext('%(languages)d language, %(average)d%% translated',
                             '%(languages)d languages, %(average)d%% translated',
                             languagecount, {"languages": languagecount, "average": average})
        },
        'description': project.description,
        'adminlink': _('Admin'),
        'languages': items,
        'instancetitle': pagelayout.get_title(),
        'topstats': topstats,
        'statsheadings': get_stats_headings(),
        'translationlegend': {'translated': _('Translations are complete'),
                    'fuzzy': _('Translations need to be checked (they are marked fuzzy)'
                    ), 'untranslated': _('Untranslated')},
    }
    
    return render_to_response('project/project.html', templatevars, context_instance=RequestContext(request))
