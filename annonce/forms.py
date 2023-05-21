
from django import forms
from django.forms import ModelForm
from ckeditor.widgets import CKEditorWidget
from .models import*

class AnnonceForm(ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model=Annonce
        fields=['content']