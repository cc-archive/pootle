from django import forms
from Pootle.conf import instance, saveprefs
from Pootle.compat.pootleauth import PootleAuth, create_user, save_users
from Pootle import storage_client
from translate.filters import checks


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
            forms.TextField(field_name="email", length=20),
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

