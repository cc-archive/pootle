from django import forms
#from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core import validators
from django.core.validators import ValidationError
from Pootle.compat.pootleauth import get_user, set_password, create_user, save_users

class CallableWrapper:
    """
    This is needed here to make the validator an object, 
    that has an attribute 'always_test' set to true.
    """
    def __init__(self, check):
        self._callable = check
        self.always_test = True

    def __call__(self, field_data, all_data):
        return self._callable(field_data, all_data)

# checks for user manipulator
def user_already_exists(field_data, all_data):
    u = get_user(field_data.strip())
    if u:
        raise ValidationError, _("User with that username already exists. Please choose another username.")
    
class RegistrationManipulator(forms.Manipulator):
    def __init__(self):
        self.fields = (
            forms.TextField(field_name="username", length=16, 
                validator_list=[CallableWrapper(user_already_exists)]),
            forms.TextField(field_name="first_name", length=16),
            forms.TextField(field_name="last_name", length=16),
            forms.TextField(field_name="email", length=16, 
                validator_list=[validators.isValidEmail]),
            forms.PasswordField(field_name="password", length=16),
            forms.PasswordField(field_name="passwordconfirm", length=16,
                validator_list=[validators.AlwaysMatchesOtherField('password', _("The two password fields didn't match."))])
            )

    def save(self, new_data):
        usernode = get_user(new_data['username'])
        if not usernode:
            usernode = create_user(new_data['username'], new_data['email'])
            usernode.name = u"%s %s" % (new_data['first_name'], new_data['last_name'])
            set_password(usernode, new_data['password'])
        if 'activationcode' in new_data:
            usernode.activationcode = new_data['activationcode']
            usernode.activated = 0
        save_users()
        return usernode
    

class ActivationManipulator(forms.Manipulator):
    def __init__(self):
        self.fields = (
            forms.TextField(field_name="username", length=16),
            forms.TextField(field_name="activationcode", length=16),
            )
    
    def save(self, data):
        usernode = get_user(data['username'])
        if usernode:
            try:
                if data['activationcode'] == usernode.activationcode:
                    usernode.activated = 1
                    usernode.__delattr__('activationcode')
                    save_users()
                return usernode.activated
            except AttributeError:
                return 0
        else:
            return 0


