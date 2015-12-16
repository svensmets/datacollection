from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class LoginForm(forms.Form):
    """ Form used to login a user
        code used from
        http://www.tangowithdjango.com/book/chapters/login.html
    """
    #http://stackoverflow.com/questions/17165147/how-can-i-make-a-django-form-field-contain-only-alphanumeric-characters
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')

    username = forms.CharField(min_length=4,max_length=30, validators=[alphanumeric])
    password = forms.CharField(widget=forms.PasswordInput())

