from django.contrib.auth.models import AbstractUser
from django.db import models
from constants import CURRENCY_CHOICES


class CustomUser(AbstractUser):
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='GBP')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
