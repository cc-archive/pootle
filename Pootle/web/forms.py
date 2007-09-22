from Pootle.web.models import UserProfile, Language
from django import newforms as forms
from django.contrib.auth.models import User
from django.newforms import Widget, Textarea, Field
from django.newforms.forms import SortedDictFromList
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.conf import settings

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
        return '<div class="foo" style="width: 30em">%s<br /><br /></div>' % force_unicode(escape(value))

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

UILANGUAGE_CHOICES = list([ (lang[0], _(lang[1])) for lang in settings.LANGUAGES])
LANGUAGES_CHOICES = list([ (lang.id, lang.name) for lang in Language.objects.all()])

class UserProfileForm(forms.Form):
    first_name = forms.CharField(_("First name"))
    last_name = forms.CharField(_("Last name"))
    email = forms.EmailField(_("Email"))
    password = forms.CharField(widget=forms.PasswordInput, label=_("Password"), required=False)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label=_("Password confirmation"), required=False)
    uilanguage = forms.ChoiceField(label=_("Interface language"), choices=UILANGUAGE_CHOICES, required=False)
    languages = forms.MultipleChoiceField(label=_("Participating languages"), required=False, widget=forms.SelectMultiple(attrs={'size':min(5, max(15, len(LANGUAGES_CHOICES)))}), choices=LANGUAGES_CHOICES)

    def __init__(self, request):
        self.user = request.user
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        if created:
            profile.save()
        if request.POST:
            data = request.POST
        else:
            data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'languages': list([lang.id for lang in profile.languages.all()]),
                'uilanguage': request.LANGUAGE_CODE,
                }
        super(UserProfileForm, self).__init__(data)

    def clean(self):
        if self.cleaned_data['password'] != self.cleaned_data['password_confirm']:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return self.cleaned_data

    def save(self):
        u = self.user
        u.first_name = self.cleaned_data['first_name']
        u.last_name = self.cleaned_data['last_name']
        u.email = self.cleaned_data['email']

        if self.cleaned_data['password']:
            u.set_password(self.cleaned_data['password'])

        profile, created = UserProfile.objects.get_or_create(user=self.user)
        for lang in Language.objects.all():
            if str(lang.id) in self.cleaned_data.get('languages'):
                profile.languages.add(Language.objects.get(pk=lang.id))
            else:
                profile.languages.remove(Language.objects.get(pk=lang.id))
        profile.save()

        return u
