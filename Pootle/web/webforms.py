from django import forms
from Pootle.web.models import UserProfile, Project, Language
from django.contrib.auth.models import User
from django.core import validators
from django.core.validators import isOnlyDigits, isValidEmail
from Pootle.utils import CallableValidatorWrapper

isValidEmail = CallableValidatorWrapper(isValidEmail)

project_choices = [(p.id, p.name) for p in Project.objects.all()]
language_choices = [(p.id, p.name) for p in Language.objects.all()]

class UserAdminManipulator(forms.Manipulator):
    def __init__(self, user):
        self.user, created = User.objects.get_or_create(username=user)
        self.fields = (
            forms.TextField(field_name="username", length=6),
            forms.TextField(field_name="first_name", length=20),
            forms.TextField(field_name="last_name", length=20),
            forms.TextField(field_name="email", length=20, validator_list=[isValidEmail]),
            forms.TextField(field_name="password", length=20),
            forms.CheckboxField(field_name="is_active"),
            forms.CheckboxField(field_name="is_superuser"),
            )

    def old_data(self):
        return dict([ (k.field_name, getattr(self.user, k.field_name)) for k in self.fields if k.field_name != 'password'])

    def save(self, new_data):
        u = self.user
        for k in ['first_name', 'last_name', 'email' ]:
            setattr(u, k, new_data[k])
        u.activated = new_data.get('is_active', False) and True
        u.is_superuser = new_data.get('is_superuser', False) and True
        if new_data['password'] != '':
            u.set_password(new_data['password'])
        u.save()

class UserProfileManipulator(forms.Manipulator):
    def __init__(self, user):
        self.user = user
        self.fields = (
            forms.TextField(field_name="first_name", length=40),
            forms.TextField(field_name="last_name", length=40),
            forms.TextField(field_name="email", length=40, validator_list=[isValidEmail]),
            forms.PasswordField(field_name="password", length=40),
            forms.PasswordField(field_name="password_confirm", length=40, 
                validator_list=[validators.AlwaysMatchesOtherField('password')]),
            forms.SelectField(field_name="uilanguage", choices=[]), # FIXME add choices
            forms.TextField(field_name="inputheight", length=10, validator_list=[isOnlyDigits]),
            forms.TextField(field_name="inputwidth", length=10, validator_list=[isOnlyDigits]),
            forms.TextField(field_name="viewrows", length=10, validator_list=[isOnlyDigits]),
            forms.TextField(field_name="translaterows", length=10, validator_list=[isOnlyDigits]),
            forms.SelectMultipleField(field_name="projects", 
                size=min(max(len(project_choices), 5), 15), choices=project_choices),
            forms.SelectMultipleField(field_name="languages", 
                size=min(max(len(language_choices), 5), 15), choices=language_choices),
        )

    def old_data(self):
        data = dict([ (k.field_name, getattr(self.user, k.field_name, None)) \
            for k in self.fields if not k.field_name.startswith("password") ])
        profile = self.user.get_profile()
        data.update({   'projects': [p.id for p in profile.projects.all()], 
                        'languages': [lang.id for lang in profile.languages.all()]} )
        return data

    def save(self, new_data):
        u = self.user
        u.first_name = new_data.get('first_name','')
        u.last_name = new_data.get('last_name', '')
        u.email = new_data['email']
        if new_data['password']:
            u.set_password(new_data['password'])
        
        try:
            profile = u.get_profile()
        except UserProfile.DoesNotExist:
            profile = UserProfile()

        for k in ['uilanguage', 'inputheight', 'inputwidth', 'viewrows', 'translaterows']:
            setattr(profile, k, new_data[k])
        
        for p in Project.objects.all():
            if str(p.id) in new_data.getlist('projects'):
                profile.projects.add(Project.objects.get(pk=p.id))
            else:
                profile.projects.remove(Project.objects.get(pk=p.id))
        
        for lang in Language.objects.all():
            if str(lang.id) in new_data.getlist('languages'):
                profile.languages.add(Language.objects.get(pk=lang.id))
            else:
                profile.languages.remove(Language.objects.get(pk=lang.id))
        profile.save()
        u.save()
        return u
