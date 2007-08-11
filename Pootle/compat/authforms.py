from django import forms
#from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core import validators
from django.core.validators import ValidationError
from Pootle.compat.pootleauth import get_user, create_user, save_users, PootleAuth
from Pootle.utils import CallableValidatorWrapper

class ActivationManipulator(forms.Manipulator):
    def __init__(self):
        self.fields = (
            forms.TextField(field_name="username", length=16),
            forms.TextField(field_name="activationcode", length=16),
            )
    
    def save(self, data):
        pa = PootleAuth()
        user = pa.get_user(data['username'])
        if user:
            try:
                if data['activationcode'] == user.activationcode:
                    user.activate()
                    save_users()
                return user.activated
            except AttributeError:
                return 0
        else:
            return 0


