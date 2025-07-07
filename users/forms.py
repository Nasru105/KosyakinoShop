from operator import le
import re
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    UserChangeForm,
)
from django import forms

from users.models import User


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
        )

    first_name = forms.CharField()
    last_name = forms.CharField()
    username = forms.CharField()
    email = forms.CharField()
    password1 = forms.CharField()
    password2 = forms.CharField()


class ProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            "image",
            "first_name",
            "last_name",
            "username",
            "phone_number",
            "email",
            "address",
        )

    image = forms.ImageField(required=False)
    first_name = forms.CharField()
    last_name = forms.CharField()
    username = forms.CharField()
    phone_number = forms.CharField(required=False)
    email = forms.CharField()
    address = forms.CharField(required=False)

    def clean_phone_number(self):
        data = self.cleaned_data["phone_number"]

        if len(data) < 11:
            raise forms.ValidationError("Номер должен содержать 11 цифр")

        if not data.isdigit():
            print(data)
            raise forms.ValidationError("Номер должен содержать только цифры")

        pattern = re.compile(r"^\d{11}$")

        if not pattern.match(data):
            raise forms.ValidationError("Неверный формат номера")

        return data
