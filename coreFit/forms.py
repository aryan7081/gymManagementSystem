from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomAdminAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.TextInput(attrs={"autofocus": True}))
