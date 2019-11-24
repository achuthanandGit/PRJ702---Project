from django import forms

from django.forms import ModelForm
from .models import Identify

class IdentifyForm(ModelForm):
    required_css_class = 'required'
    class Meta:
        model = Identify
        fields = [
            'pitTag', 'tank', 'username', 'image'
       ]


    