from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomerForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]

    def clean_username(self):
        data = self.cleaned_data["username"].strip()
        return data
