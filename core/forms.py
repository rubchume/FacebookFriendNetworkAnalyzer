from django import forms


class LogInForm(forms.Form):
    user = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput())
