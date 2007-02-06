from django import forms
from Pootle.conf import instance, saveprefs
from Pootle.compat.pootleauth import PootleAuth, create_user, save_users
from Pootle import storage_client
from translate.filters import checks
from django.core import validators
from django.core.validators import isOnlyDigits, isValidEmail
from Pootle.utils import CallableValidatorWrapper

isValidEmail = CallableValidatorWrapper(isValidEmail)

CHECKS = [ ('Standard', 'Standard')] + [ (ch, ch) for ch in checks.projectcheckers.keys()]
# FIXME: Filetypes should probably be provided by translate-toolkit.
FILETYPES = [
    ('po', 'po'),
    ('xliff','xliff'),
    ]

class SiteOptionsManipulator(forms.Manipulator):
    def __init__(self):
        self.fields = (
            forms.TextField(field_name="title", length=40),
            forms.LargeTextField(field_name="description"),
            forms.TextField(field_name="baseurl", length=40),
            forms.TextField(field_name="homepage", length=40),
          )

    def old_data(self):
        return dict([ (optionname.field_name, getattr(instance(), optionname.field_name, "")) for optionname in self.fields])

    def save(self, new_data):
        for optionname in self.fields:
            setattr(instance(), optionname.field_name, new_data[optionname.field_name])
        saveprefs()
        

class UserAdminManipulator(forms.Manipulator):
    def __init__(self):
        self.fields = (
            forms.TextField(field_name="username", length=6),
            forms.TextField(field_name="name", length=20),
            forms.TextField(field_name="email", length=20, validator_list=[isValidEmail]),
            forms.TextField(field_name="password", length=20),
            forms.CheckboxField(field_name="activated"),
            )

    def old_data(self, user):
        pa = PootleAuth()
        u = pa.get_user(user)
        if u:
            return dict([ (k.field_name, getattr(u,k.field_name)) for k in self.fields if k.field_name != 'password'])
        else:
            return {}

    def save(self, new_data):
        pa = PootleAuth()
        user = pa.get_user(new_data['username'])
        if not user:
            user = create_user(new_data['username'], new_data['email'])
        user.set_user(new_data)
        save_users()

class ProjectAdminManipulator(forms.Manipulator):
    def __init__(self):
        self.fields = (
            forms.TextField(field_name="name", length=40),
            forms.LargeTextField(field_name="description"),
            forms.SelectField(field_name="checkerstyle", choices=CHECKS),
            forms.SelectField(field_name="filetype", choices=FILETYPES),
            forms.CheckboxField(field_name="create_mo_files"),
            )

    def old_data(self, project):
        p = storage_client.ProjectWrapper(project)
        return dict([ (k.field_name, getattr(p,k.field_name)) for k in self.fields ])

    def save(self, new_data, projectcode):
        p = storage_client.ProjectWrapper(projectcode)
        for k in self.fields:
            setattr(p, k.field_name, new_data[k.field_name])

class UserProfileManipulator(forms.Manipulator):
    def __init__(self, user):
        self.user = user
        project_choices = [(p.code, p.name) for p in storage_client.get_project_objects()]
        language_choices = [(p.code, p.name) for p in storage_client.get_language_objects()]
        self.fields = (
            forms.TextField(field_name="name", length=40),
            forms.TextField(field_name="email", length=40, validator_list=[isValidEmail]),
            forms.PasswordField(field_name="password", length=40),
            forms.PasswordField(field_name="password_confirm", length=40, validator_list=[validators.AlwaysMatchesOtherField('password')]),
            forms.SelectField(field_name="uilanguage", choices=[]), # FIXME add choices
            forms.TextField(field_name="inputheight", length=10, validator_list=[isOnlyDigits]),
            forms.TextField(field_name="inputwidth", length=10, validator_list=[isOnlyDigits]),
            forms.TextField(field_name="viewrows", length=10, validator_list=[isOnlyDigits]),
            forms.TextField(field_name="translaterows", length=10, validator_list=[isOnlyDigits]),
            forms.SelectMultipleField(field_name="projects", size=min(max(len(project_choices), 5), 15), choices=project_choices),
            forms.SelectMultipleField(field_name="languages", size=min(max(len(language_choices), 5), 15), choices=language_choices),
        )

    def old_data(self):
        return dict([ (k.field_name, getattr(self.user, k.field_name, None)) for k in self.fields if not k.field_name.startswith("password") ])

    def save(self, new_data):
        u = self.user
        u.set_user(new_data)
        u.projects = new_data.getlist('projects')
        u.languages = new_data.getlist('languages')
        u.save()
        return u
