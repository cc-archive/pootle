from django import forms
#from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core import validators
from django.core.validators import ValidationError
from Pootle.compat.pootleauth import get_user, create_user, save_users, PootleAuth
from Pootle.utils import CallableValidatorWrapper

# checks for user manipulator
def user_already_exists(field_data, all_data):
    u = get_user(field_data.strip())
    if u:
        raise ValidationError, _("User with that username already exists. Please choose another username.")
    
class RegistrationManipulator(forms.Manipulator):
    def __init__(self):
        self.fields = (
            forms.TextField(field_name="username", length=16, 
                validator_list=[CallableValidatorWrapper(user_already_exists)]),
            forms.TextField(field_name="first_name", length=16),
            forms.TextField(field_name="last_name", length=16),
            forms.TextField(field_name="email", length=16, 
                validator_list=[validators.isValidEmail]),
            forms.PasswordField(field_name="password", length=16),
            forms.PasswordField(field_name="passwordconfirm", length=16,
                validator_list=[validators.AlwaysMatchesOtherField('password', _("The two password fields didn't match."))])
            )

    def save(self, new_data):
        pa = PootleAuth()
        user = pa.get_user(new_data['username'])
        if not user:
            user = create_user(new_data['username'], new_data['email'])
            user.set_user({
                'name': u"%s %s" % (new_data['first_name'], new_data['last_name']),
                'password': new_data['password'],
                'activationcode': new_data['activationcode'],
                'activated': 0, })
        save_users()
        return user

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


