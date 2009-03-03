from django.http import Http404
from django.forms.models import modelformset_factory, BaseModelFormSet
from django import forms
from django.forms.formsets import ManagementForm
from django.utils.translation import ugettext as _
from django.conf import settings

from Pootle import pan_app, indexpage, adminpages, projects

from pootle_app.views.auth          import redirect
from pootle_app.views.util          import render_to_kid, render_jtoolkit, \
    KidRequestContext, init_formset_from_data, choices_from_models, selected_model
from pootle_app.core                import Language, Project
from pootle_app.translation_project import TranslationProject
from pootle_app                     import project_tree

def user_can_admin_project(f):
    def decorated_f(request, project_code, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('/projects/%s' % project_code, message=_("Only administrators may modify the project options."))
        else:
            return f(request, project_code, *args, **kwargs)
    return decorated_f

def get_project(f):
    def decorated_f(request, project_code, *args, **kwargs):
        try:
            project = Project.objects.get(code=project_code)
            return f(request, project, *args, **kwargs)
        except Project.DoesNotExist:
            return redirect('/', message=_("The project %s is not defined for this Pootle installation" % project_code))
    return decorated_f

@get_project
def project_language_index(request, project, _path_var):
    return render_jtoolkit(indexpage.ProjectLanguageIndex(project, request))

class LanguageForm(forms.ModelForm):
    update = forms.BooleanField(required=False)

    class Meta:
        prefix="existing_language"        

LanguageFormset = modelformset_factory(Language, LanguageForm, fields=['update'], extra=0)

def make_new_language_form(existing_languages, post_vars=None):
    new_languages = [language for language in Language.objects.all() if not language in set(existing_languages)]

    class NewLanguageForm(forms.Form):
        add_language = forms.ChoiceField(choices=choices_from_models(new_languages), label=_("Add language"))

    return NewLanguageForm(post_vars)

def process_post(request, project):
    def process_existing_languages(request, project):
        formset = init_formset_from_data(LanguageFormset, request.POST)
        if formset.is_valid():
            for form in formset.forms:
                if form['update'].data:
                    language = form.instance
                    translation_project = TranslationProject.objects.get(language=language, project=project)
                    translation_project.converttemplates(request)
        return formset

    def process_new_language(request, project, languages):
        new_language_form = make_new_language_form(languages, request.POST)

        if new_language_form.is_valid():
            new_language = selected_model(Language, new_language_form['add_language'])
            if new_language is not None:
                projects.add_translation_project(new_language, project)

    if request.method == 'POST':
        formset = process_existing_languages(request, project)
        process_new_language(request, project, [form.instance for form in formset.forms])

def process_get(request, project):
    if request.method == 'GET':
        try:
            language_code = request.GET['updatelanguage']
            translation_project = Translation.objects.get(language__code=language_code, project=project)
            if 'initialize' in request.GET:
                translation_project.initialize(request, language_code)
            elif 'doupdatelanguage' in request.GET:
                translation_project.converttemplates(request)
        except KeyError:
            pass

@user_can_admin_project
def project_admin(request, project_code):
    project = Project.objects.get(code=project_code)

    process_get(request, project)
    process_post(request, project)

    existing_languages = project_tree.get_languages(project)
    formset = LanguageFormset(queryset=existing_languages)
    new_language_form = make_new_language_form(existing_languages)

    template_vars = {
        "pagetitle":          _("Pootle Admin: %s") % project.fullname,
        "norights_text":      _("You do not have the rights to administer this project."),
        "project":            project,
        "iso_code":           _("ISO Code"),
        "full_name":          _("Full Name"),
        "existing_title":     _("Existing languages"),
        "formset":            formset,
        "new_language_form":  new_language_form,
        "update_button":      _("Update Languages"),
        "add_button":         _("Add Language"),
        "main_link":          _("Back to main page"),
        "update_link":        _("Update from templates"), 
        "initialize_link":    _("Initialize"),
        "instancetitle":      pan_app.get_title() 
        }

    return render_to_kid("projectadmin.html", KidRequestContext(request, template_vars))

def projects_index(request, path):
    return render_jtoolkit(indexpage.ProjectsIndex(request))
