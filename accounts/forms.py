from django import forms
from django.core.exceptions import ValidationError
from .models import User


class RegisterForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=8
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "password",
        ]


    def clean_email(self):

        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")

        return email


    def clean(self):

        cleaned = super().clean()

        password = cleaned.get("password")
        confirm = cleaned.get("confirm_password")

        if password != confirm:
            raise ValidationError("Passwords do not match")

        return cleaned