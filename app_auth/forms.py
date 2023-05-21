from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from eab.models import*

class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'password1',
            'password2'
        ]

        labels={
            'first_name':'Prénom', 
            'last_name':'Nom', 
            'username':'Nom utilisateur', 
            'email':'Email', 
            'password1':'Mot de passe',
            'password2':'Conf mot de passe'
        }

        widgets={
            'last_name':forms.TextInput(attrs={'class':'design','required':True}),
            'first_name':forms.TextInput(attrs={'class':'design','required':True}),
            'username':forms.TextInput(attrs={'class':'design','required':True}),
            'email':forms.TextInput(attrs={'class':'design','required':True}),
            'password1':forms.PasswordInput(attrs={'required':True}),
            'password2':forms.PasswordInput(attrs={'required':True})
            
        }

class LoginForm(forms.Form):
    username=forms.CharField(label="Nom utilisateur", widget=forms.TextInput(attrs={'class':'form-control'}))
    password=forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={'class':'form-control'}))

class ProfileForm(forms.ModelForm):
    class Meta:
        model=Profile
        fields=['photo']

class PasswordChangingForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for fieldname in ['old_password','new_password1','new_password2']:
            self.fields[fieldname].widget.attrs = {'class':'form-control'}