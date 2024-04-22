from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser  # Ensure this import reflects your project structure
from constants import CURRENCY_CHOICES


class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    currency = forms.ChoiceField(choices=CURRENCY_CHOICES, initial='GBP')

    class Meta:
        model = CustomUser
        fields = ["username", "email", "currency", "password1", "password2"]