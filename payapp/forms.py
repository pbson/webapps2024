from django import forms
from .models import Transaction, PaymentRequest
from register.models import CustomUser as User


class SendMoneyForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['recipient', 'amount', 'currency']
        labels = {
            'recipient': 'Recipient Username',
            'amount': 'Amount to Send',
            'currency': 'Currency',
        }
        widgets = {
            'recipient': forms.Select(attrs={'class': 'form-control'}),
            'currency': forms.Select(attrs={'class': 'form-control'}),
        }

    # Exclude admin and current user from the recipient field's queryset
    def __init__(self, *args, **kwargs):
        # Get the user argument and remove it from kwargs
        self.user = kwargs.pop('user', None)

        super(SendMoneyForm, self).__init__(*args, **kwargs)
        self.fields['recipient'].queryset = User.objects.filter(is_staff=False, is_superuser=False).exclude(id=self.user.id)


class RequestMoneyForm(forms.ModelForm):
    class Meta:
        model = PaymentRequest
        fields = ['recipient', 'amount', 'currency']
        labels = {
            'recipient': 'Request From (Username)',
            'amount': 'Requested Amount',
            'currency': 'Currency',
        }
        widgets = {
            'recipient': forms.Select(attrs={'class': 'form-control'}),
            'currency': forms.Select(attrs={'class': 'form-control'}),
        }

    # Exclude admin and current user from the recipient field's queryset
    def __init__(self, *args, **kwargs):
        # Get the user argument and remove it from kwargs
        self.user = kwargs.pop('user', None)

        super(RequestMoneyForm, self).__init__(*args, **kwargs)
        self.fields['recipient'].queryset = User.objects.filter(is_staff=False, is_superuser=False).exclude(id=self.user.id)
