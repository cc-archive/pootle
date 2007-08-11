from django import newforms as forms
from django.newforms.forms import SortedDictFromList
from django.newforms.widgets import Widget, Textarea
from django.newforms.fields import Field
from django.utils.encoding import force_unicode

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

