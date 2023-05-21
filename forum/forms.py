from django import forms
from django.forms import ModelForm
from ckeditor.widgets import CKEditorWidget
from .models import*

class QuestionForm(ModelForm):
    content = forms.CharField(widget=CKEditorWidget(attrs={'class':'form-control','required':True}))
    class Meta:
        model=Question
        fields=['content']

class AnswerForm(ModelForm):
    content = forms.CharField(widget=CKEditorWidget(attrs={'class':'form-control','required':True}))
    class Meta:
        model=Answer
        fields=['content']