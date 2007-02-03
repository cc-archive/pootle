from django import forms
from Pootle.conf import instance, saveprefs

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
        

