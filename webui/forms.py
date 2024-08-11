from django import forms 
from django.contrib.auth.models import User 
from django.contrib.auth.forms import UserCreationForm 
from webui.models import Profile_User


class user_register_form(UserCreationForm):
    email = forms.EmailField() 

    class Meta:
        model = User 
        fields = ['username', 'email', 'password1', 'password2']
        

class user_update_form(forms.ModelForm):
    email = forms.EmailField() 

    class Meta:
        model = User 
        fields = ['username', 'email']


class profile_update_form(forms.ModelForm):
    class Meta:
        model = Profile_User 
        fields = ['image']