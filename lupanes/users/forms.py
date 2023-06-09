from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class AuthForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())

    def clean_password(self):
        data = self.cleaned_data["password"]
        if data != settings.LUPIERRA_BASIC_AUTH_PASS:
            raise ValidationError("Contraseña incorrecta")
        return data


class CustomerForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]

    def clean_username(self):
        data = self.cleaned_data["username"].strip()
        return data
