from django import forms
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _


class LoginForm(forms.Form):
    username = forms.CharField(
        label=_("Username"),
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Username"),
            }
        ),
    )

    password = forms.CharField(
        label=_("Password"),
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": _("Password"),
            }
        ),
    )

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if not authenticate(username=username, password=password):
            raise forms.ValidationError(_("Provided credentials are invalid."))

        return cleaned_data
