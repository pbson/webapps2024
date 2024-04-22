from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from helpers import convert_currency
import requests


@csrf_protect
def register_user(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            # Set initial balance in GBP
            initial_balance_gbp = 1000
            selected_currency = form.cleaned_data['currency']

            # Convert balance if necessary
            if selected_currency in ['EUR', 'USD']:
                api_url = f"http://localhost:8000/conversion/GBP/{selected_currency}/{initial_balance_gbp}"
                response = requests.get(api_url)
                if response.status_code == 200:
                    conversion_result = response.json()
                    user.balance = conversion_result['converted_amount']
                else:
                    messages.error(request, "Currency conversion failed. Setting balance in GBP.")
                    user.balance = initial_balance_gbp
            else:
                user.balance = initial_balance_gbp

            user.save()

            login(request, user)
            messages.success(request, "User created successfully.")
            return redirect('home')
        else:
            for msg in form.errors:
                messages.error(request, form.errors[msg])
            return render(request, 'register/register.html', {'register_user': form})
    else:
        if request.user.is_authenticated:
            return redirect('home')
        form = RegisterForm()
        return render(request, 'register/register.html', {'register_user': form})


@csrf_protect
def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'register/login.html', {'login_user': form})
    else:
        if request.user.is_authenticated:
            return redirect('home')
        form = AuthenticationForm()
        return render(request, 'register/login.html', {'login_user': form})


@csrf_protect
def logout_user(request):
    logout(request)
    return redirect('login')
