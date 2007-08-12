from django import newforms as forms
from django.newforms import Widget, Textarea, Field
from django.newforms.forms import SortedDictFromList
from django.utils.encoding import force_unicode
from django.contrib.auth.models import User
from Pootle.web.models import UserProfile

class TranslationFormBase(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput())

    def get_target_list(self):
        return list([(int(k.strip("plural_")), v) for k, v in self.cleaned_data.iteritems() if k.startswith("plural_")])

def translation_form_factory(num_plural=1, rows=3):
    """
    Returns form with specified number of plural fields.
    This is needed because languages have different number of plurals.
    """
    class TranslationForm(TranslationFormBase):
        pass
    textfield = lambda x: forms.CharField(label=x, widget=Textarea(attrs={'cols':'50', 'rows': str(rows)}))
    
    base = TranslationForm.base_fields.items()
    if num_plural == 1:
        plural_fields = [
            ('source', StaticField(label=_("Original"))), 
            ('translation', textfield(_("Translation")))
            ]
    else:
        plural_fields = [
            ('source', StaticField(label=_("Singular"))), 
            ('source_plural', StaticField(label=_("Plural"))) ]
        plural_fields += [('plural_%d' % x, textfield(_("Plural form %d") % x)) for x in range(num_plural)]

    TranslationForm.base_fields =  SortedDictFromList(base+plural_fields)
    return TranslationForm


class StaticWidget(Widget):
    def __init__(self):
        self.attrs = {}

    def render(self, name, value, attrs=None):
        if value is None: value = ''
        return '<div class="foo" style="width: 30em">%s<br /><br /></div>' % force_unicode(value)

class StaticField(Field):
    widget = StaticWidget
    required = False

    def __init__(self, label, help_text=None):
        self.label = label
        self.help_text = help_text
        self.widget = self.widget()

class RegistrationForm(forms.Form):
    username = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    passwordconfirm = forms.CharField(label=_("Password (confirm)"), widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
            raise forms.ValidationError(_("User with that username already exists. Please choose another username."))
        except User.DoesNotExist:
            return username

    def clean(self):
        if self.cleaned_data['password'] != self.cleaned_data['passwordconfirm']:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return self.cleaned_data

    def save(self):
        if self.errors:
            raise ValueError(_("User info is not valid."))
        user_dict = self.cleaned_data.copy()
        del user_dict['passwordconfirm']
        u = User(**user_dict)
        u.set_password(user_dict['password'])
        u.save()
        profile = UserProfile(user=u)
        profile.save()
        return u


class ActivationForm(forms.Form):
    username = forms.CharField()
    activationcode = forms.CharField()

    def save(self):
        try:
            u = User.objects.get(username=self.cleaned_data['username'])
        except User.DoesNotExist:
            pass

        code = u.get_profile().activation_code
        # empty activation code disables activation
        if code and code == self.cleaned_data['activationcode']:
            u.is_active = True
            u.save()
            profile = u.get_profile()
            profile.activation_code = ''
            profile.save()
            return u
        else:
            return None

