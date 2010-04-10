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

import os

from translate.storage.xliff import xlifffile

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.core.exceptions import PermissionDenied

from pootle_misc.baseurl import redirect
from pootle_app.models.permissions import get_matching_permissions, check_permission
from pootle_misc.util import paginate
from pootle_profile.models import get_profile

from pootle_store.models import Store, Unit
from pootle_store.forms import unit_form_factory, SearchForm

def export_as_xliff(request, pootle_path):
    #FIXME: cache this
    if pootle_path[0] != '/':
        pootle_path = '/' + pootle_path
    store = get_object_or_404(Store, pootle_path=pootle_path)

    outputstore = store.convert(xlifffile)
    outputstore.switchfile(store.name, createifmissing=True)
    encoding = getattr(store.file.store, "encoding", "UTF-8")
    content_type = "application/x-xliff; charset=UTF-8"
    response = HttpResponse(str(outputstore), content_type=content_type)
    filename, ext = os.path.splitext(store.name)
    filename += os.path.extsep + 'xlf'
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response

def download(request, pootle_path):
    if pootle_path[0] != '/':
        pootle_path = '/' + pootle_path
    store = get_object_or_404(Store, pootle_path=pootle_path)
    store.sync(update_translation=True, create=True)
    return redirect('/export/' + store.real_path)

####################### Translate Page ##############################

def get_search_step_query(translation_project, form, units_queryset):
    """Narrows down units query to units matching search string"""
    if translation_project.indexer is None:
        return None

    searchparts = []
    for word in form.cleaned_data['search'].split():
        # Generate a list for the query based on the selected fields
        querylist = [(field, word) for field in form.cleaned_data['sfields']]
        textquery = translation_project.indexer.make_query(querylist, False)
        searchparts.append(textquery)

    paths = units_queryset.order_by().values_list('store__pootle_path', flat=True).distinct()
    querylist = [('pofilename', pootle_path) for pootle_path in paths.iterator()]
    pathquery = translation_project.indexer.make_query(querylist, False)
    searchparts.append(pathquery)
    limitedquery = translation_project.indexer.make_query(searchparts, True)
    result = translation_project.indexer.search(limitedquery, ['dbid'])
    dbids = (int(item['dbid'][0]) for item in result)
    return units_queryset.filter(id__in=dbids)

def get_step_query(request, units_queryset):
    """Narrows down unit query to units matching conditions in GET and POST"""
    if 'unit' in request.GET or 'page' in request.GET:
        return units_queryset

    if 'unitstates' in request.GET:
        unitstates = request.GET['unitstates'].split(',')
        if unitstates:
            state_queryset = units_queryset.none()
            for unitstate in unitstates:
                if unitstate == 'untranslated':
                    state_queryset = state_queryset | units_queryset.filter(target_length=0)
                elif unitstate == 'translated':
                    state_queryset = state_queryset | units_queryset.filter(target_length__gt=0, fuzzy=False)
                elif unitstate == 'fuzzy':
                    state_queryset = state_queryset | units_queryset.filter(fuzzy=True)
            units_queryset = state_queryset

    if 'matchnames' in request.GET:
        matchnames = request.GET['matchnames'].split(',')
        if matchnames:
            match_queryset = units_queryset.none()
            if 'hassuggestion' in matchnames:
                match_queryset = units_queryset.exclude(suggestion=None)
                matchnames.remove('hassuggestion')
            if matchnames:
                match_queryset = match_queryset | units_queryset.filter(qualitycheck__name__in=matchnames)
            units_queryset = match_queryset

    return units_queryset.distinct()

def get_current_units(request, step_queryset):
    """returns current active unit, and in case of POST previously active unit"""
    edit_unit = None
    prev_unit = None
    pager = None
    # GET gets priority
    if 'unit' in request.GET:
        # load a specific unit in GET
        try:
            edit_id = int(request.GET['unit'])
            edit_unit = step_queryset.get(id=edit_id)
        except (Unit.DoesNotExist, ValueError):
            pass
    elif 'page' in request.GET:
        # load first unit in a specific page
        pager = paginate(request, step_queryset, items=10)
        edit_unit = pager.object_list[0]
    elif 'id' in request.POST and 'index' in request.POST:
        # GET doesn't specify a unit try POST
        prev_id = int(request.POST['id'])
        prev_index = int(request.POST['index'])
        pootle_path = request.POST['pootle_path']
        back = request.POST.get('back', False)
        if back:
            queryset = (step_queryset.filter(store__pootle_path=pootle_path, index__lte=prev_index) | \
                        step_queryset.filter(store__pootle_path__lt=pootle_path)
                        ).order_by('-store__pootle_path', '-index')
        else:
            queryset = (step_queryset.filter(store__pootle_path=pootle_path, index__gte=prev_index) | \
                        step_queryset.filter(store__pootle_path__gt=pootle_path)
                        ).order_by('store__pootle_path', 'index')

        for unit in queryset.iterator():
            if edit_unit is None and prev_unit is not None:
                edit_unit = unit
                break
            if unit.id == prev_id:
                prev_unit = unit
        if edit_unit is None and prev_unit is not None:
            # probably prev_unit was last unit in chain.
            #FIXME: maybe we want to retain the show end of query behavior?
            if back:
                edit_unit = prev_unit
            else:
                raise StopIteration

    if edit_unit is None:
        # all methods failed, get first unit in queryset
        edit_unit = step_queryset.iterator().next()

    return prev_unit, edit_unit, pager

def translate_end(request, translation_project):
    """render a message at end of review, translate or search action"""
    if request.POST:
        # end of iteration
        if 'matchnames' in request.GET:
            message = _("No more matching strings to review.")
        else:
            message = _("No more matching strings to translate.")
    else:
        if 'matchnames' in request.GET:
            message = _("No matching strings to review.")
        else:
            message = _("No matching strings to translate.")

    context = {
        'endmessage': message,
        'translation_project': translation_project,
        }
    return render_to_response('store/translate_end.html', context, context_instance=RequestContext(request))


def translate_page(request, units_queryset):
    cantranslate = check_permission("translate", request)
    cansuggest = check_permission("suggest", request)
    translation_project = request.translation_project
    language = translation_project.language

    step_queryset = None

    # Process search first
    search_form = None
    if 'search' in request.GET and 'sfields' in request.GET:
        search_form = SearchForm(request.GET)
        if search_form.is_valid():
            step_queryset = get_search_step_query(request.translation_project, search_form, units_queryset)
    else:
        search_form = SearchForm()

    # which units are we interested in?
    if step_queryset is None:
        step_queryset = get_step_query(request, units_queryset)

    try:
        prev_unit, edit_unit, pager = get_current_units(request, step_queryset)
    except StopIteration:
        return translate_end(request, translation_project)

    # time to process POST submission
    form = None
    if prev_unit is not None and ('submit' in request.POST or 'suggest' in request.POST):
        # check permissions
        if 'submit'  in request.POST and not cantranslate or \
           'suggest' in request.POST and not cansuggest:
            raise PermissionDenied

        form_class = unit_form_factory(language, len(prev_unit.source.strings))
        form = form_class(request.POST, instance=prev_unit)
        if form.is_valid():
            if cantranslate and 'submit' in request.POST:
                form.save()
            elif cansuggest:
                prev_unit.add_suggestion(form.cleaned_data['target_f'], get_profile(request.user))
        else:
            # form failed, don't skip to next unit
            edit_unit = prev_unit

    # only create form for edit_unit if prev_unit was processed successfully
    if form is None or form.is_valid():
        form_class = unit_form_factory(language, len(edit_unit.source.strings))
        form = form_class(instance=edit_unit)

    if pager is None:
        store = edit_unit.store
        page = store.units.filter(index__lt=edit_unit.index).count() / 10 + 1
        pager = paginate(request, store.units, items=10, page=page)

    # caluclate url querystring so state is retained on POST
    # we can't just use request URL cause unit and page GET vars cancel state
    GET_vars = []
    for key, values in request.GET.iterlists():
        if key not in ('page', 'unit'):
            for value in values:
                GET_vars.append('%s=%s' % (key, value))

    context = {
        'form': form,
        'search_form': search_form,
        'unit': edit_unit,
        'store': store,
        'pager': pager,
        'language': language,
        'translation_project': store.translation_project,
        'GET_state': '&'.join(GET_vars),
        }
    return render_to_response('store/translate.html', context, context_instance=RequestContext(request))

def translate(request, pootle_path):
    if pootle_path[0] != '/':
        pootle_path = '/' + pootle_path
    store = get_object_or_404(Store, pootle_path=pootle_path)
    request.translation_project = store.translation_project
    request.permissions = get_matching_permissions(get_profile(request.user), request.translation_project.directory)

    return translate_page(request, store.units)
