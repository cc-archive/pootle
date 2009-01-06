#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright 2008 Zuza Software Foundation
# 
# This file is part of Pootle.
#
# Pootle is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# Pootle is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pootle; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect

from Pootle import indexpage, pan_app, translatepage, projects
from Pootle.misc.jtoolkit_django import process_django_request_args

from Pootle.views.util import render_to_kid
from Pootle.views.util import render_jtoolkit

def check_language(f):
    def decorated_f(request, language_code, *args, **kwargs):
        if language_code == "templates" or pan_app.get_po_tree().haslanguage(language_code):
            return f(request, language_code, *args, **kwargs)
        else:
            request.session['message'] = "The language %s is not defined for this Pootle installation" % language_code
            return HttpResponseRedirect('/')
    return decorated_f

def check_project(f):
    def decorated_f(request, language_code, project_code, *args, **kwargs):
        if pan_app.get_po_tree().hasproject(language_code, project_code):
            return f(request, language_code, project_code, *args, **kwargs)
        else:
            request.session['message'] = "The project %s does not exist for the language %s" % (project_code, language_code)
            return HttpResponseRedirect('/%s' % language_code)
    return decorated_f

def check_language_and_project(f):
    return check_project(check_language(f))

@check_language
def language_index(request, language_code):
    return render_jtoolkit(indexpage.LanguageIndex(language_code, request))

@check_language_and_project
def translation_project_admin(request, language_code, project_code):
    return render_jtoolkit(adminpages.TranslationProjectAdminPage(project_code, request, process_django_request_args(request)))

@check_language_and_project
def translate_page(request, language_code, project_code, dirfilter):
    try:
        if dirfilter is None:
            dirfilter = ""
        return render_jtoolkit(translatepage.TranslatePage(project_code, request, process_django_request_args(request), dirfilter))
    except projects.RightsError, msg:
        request.session['message'] = msg
        return render_jtoolkit(indexpage.ProjectIndex(pan_app.get_po_tree().getproject(language_code, project_code), 
                                                      request, process_django_request_args(request)))

@check_language_and_project
def project_index(request, language_code, project_code):
    try:
        return render_jtoolkit(indexpage.ProjectIndex(pan_app.get_po_tree().getproject(language_code, project_code),
                                                      request, process_django_request_args(request)))
    except projects.RightsError, msg:
        request.session['message'] = msg
        return render_jtoolkit(indexpage.PootleIndex(request))

def handle_translation_file(request, arg_dict, project, language_code, project_code, file_path):
    # Don't get confused here. request.GET contains HTTP
    # GET vars while get is a dictionary method
    if request.GET.get("translate", 0):
        try:
            return render_jtoolkit(translatepage.TranslatePage(project, request, process_django_request_args(request),
                                                               dirfilter=file_path))
        except projects.RightsError, stoppedby:
            pathwords = file_path.split(os.sep)
            if len(pathwords) > 1:
                dirfilter = os.path.join(*pathwords[:-1])
            else:
                dirfilter = ""
            request.session['message'] = stoppedby
            return indexpage.ProjectIndex(project, request, process_django_request_args(request), dirfilter=dirfilter)
    # Don't get confused here. request.GET contains HTTP
    # GET vars while get is a dictionary method
    elif request.GET.get("index", 0):
        return indexpage.ProjectIndex(project, request, process_django_request_args(request), dirfilter=file_path)
    else:
        pofile = project.getpofile(pofilename, freshen=False)
        encoding = getattr(pofile, "encoding", "UTF-8")
        content_type = "text/plain; charset=%s" % encoding
        return HttpResponse(open(pofile.filename).read(), content_type=content_type)

def handle_alternative_format(request, language_code, project_code, file_path):
    basename, extension = os.path.splitext(file_path)
    pofilename = basename + os.extsep + project.fileext
    extension = extension[1:]
    if extension == "mo":
        if not "pocompile" in project.getrights(session):
            return None
    etag, filepath_or_contents = project.convert(pofilename, extension)
    if etag:
        contents = open(filepath_or_contents).read()
    else:
        contents = filepath_or_contents
    content_type = ""
    if extension == "po":
        content_type = "text/x-gettext-translation; charset=UTF-8"
    elif extension == "csv":
        content_type = "text/csv; charset=UTF-8"
    elif extension == "xlf":
        content_type = "application/x-xliff; charset=UTF-8"
    elif extension == "ts":
        content_type = "application/x-linguist; charset=UTF-8"
    elif extension == "mo":
        content_type = "application/x-gettext-translation"
    return HttpResponse(contents, content_type=content_type)

def handle_zip(request, arg_dict, language_code, project_code, file_path):
    if not "archive" in project.getrights(request):
        return None
    if len(pathwords) > 1:
        pathwords = file_path.split(os.sep)
        dirfilter = os.path.join(*pathwords[:-1])
    else:
        dirfilter = None
    goal = arg_dict.get("goal", None)
    if goal:
        goalfiles = project.getgoalfiles(goal)
        pofilenames = []
        for goalfile in goalfiles:
            pofilenames.extend(project.browsefiles(goalfile))
    else:
        pofilenames = project.browsefiles(dirfilter)
    archivecontents = project.getarchive(pofilenames)
    return HttpResponse(archivecontents, content_type="application/zip")

def handle_sdf(request, language_code, project_code, file_path):
    if not "pocompile" in project.getrights(session):
        return None
    return HttpResponse(project.getoo(), content_type="text/tab-seperated-values")

@check_language_and_project
def handle_file(request, language_code, project_code, file_path):
    arg_dict = process_django_request_args(request)
    project = pan_app.get_po_tree().getproject(language_code, project_code)
    if file_path.endswith("." + project.fileext):
        return handle_translation_file(request, arg_dict, project, language_code, project_code, file_path)
    elif bottom.endswith(".csv") or bottom.endswith(".xlf") or \
         bottom.endswith(".ts") or bottom.endswith(".po") or \
         bottom.endswith(".mo"):
        return handle_alternative_format(request, language_code, project_code, file_path)
    elif bottom.endswith(".zip"):
        return handle_zip(request, arg_dict, language_code, project_code, file_path)
    elif bottom.endswith(".sdf") or bottom.endswith(".sgi"):
        return handle_sdf(request, language_code, project_code, file_path)
    else:
        return indexpage.ProjectIndex(project, request, arg_dict, file_path)
