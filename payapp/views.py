from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction, OperationalError
from django.db.models import Case, When, Value, CharField, Q
from django.utils import timezone
from decimal import Decimal
from .forms import SendMoneyForm, RequestMoneyForm
from helpers import convert_currency
from register.models import CustomUser as User
from .models import Transaction, PaymentRequest
from django.http import JsonResponse
from timestampservice.timestampclient import TimestampClient


def get_timestamp():
    timestamp_client = TimestampClient()
    timestamp = timestamp_client.get_current_timestamp()
    if timestamp:
        return JsonResponse({'timestamp': timestamp})
    else:
        return JsonResponse({'error': 'Unable to fetch timestamp'}, status=500)
def process_transaction(request, sender, recipient, amount, currency):
    recipient = User.objects.get(username=recipient)

    # Convert amount to sender's currency
    amount_in_sender_currency = Decimal(amount)
    if currency != sender.currency:
        converted_amount = convert_currency(request, currency, sender.currency, amount)
        amount_in_sender_currency = Decimal(converted_amount)

    # Check if sender has enough balance
    if sender.balance < amount_in_sender_currency:
        raise ValueError("Insufficient balance.")

    # Update sender balance
    sender.balance -= amount_in_sender_currency

    # Convert amount to recipient's currency
    amount_in_recipient_currency = Decimal(amount)
    if currency != recipient.currency:
        converted_amount = convert_currency(request, currency, recipient.currency, amount)
        amount_in_recipient_currency = Decimal(converted_amount)

    # Update recipient balance
    recipient.balance += amount_in_recipient_currency

    # Save changes to sender, recipient
    sender.save()
    recipient.save()

    # Create and save the transaction
    Transaction.objects.create(
        sender=sender,
        recipient=recipient,
        amount=amount,
        currency=currency,
        timestamp=get_timestamp(),
    )

@csrf_protect
def home(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.is_superuser:
        return redirect('admin:index')

    user_balance = request.user.balance
    user_transactions = Transaction.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).order_by('-timestamp')
    user_payment_requests = PaymentRequest.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).annotate(
        custom_order=Case(
            When(status='PENDING', then=Value(1)),
            default=Value(2),
            output_field=CharField(),
        )
    ).order_by('custom_order', '-timestamp')

    context = {
        'user_balance': user_balance,
        'transactions': user_transactions,
        'payment_requests': user_payment_requests,
    }

    return render(request, 'payapp/home.html', context)

@csrf_protect
@login_required
def send_money(request):
    if request.method == 'POST':
        form = SendMoneyForm(request.POST, user=request.user)
        if form.is_valid():
            new_transaction = form.save(commit=False)

            # Check if amount is positive
            if new_transaction.amount <= 0:
                messages.error(request, 'Transaction failed: Amount must be positive.')
                return render(request, 'payapp/send_money.html', {'form': form})

            # Check if the recipient exists
            try:
                recipient = User.objects.get(username=new_transaction.recipient)
            except User.DoesNotExist:
                messages.error(request, 'Recipient does not exist.')
                return render(request, 'payapp/send_money.html', {'form': form})

            # Perform transaction
            try:
                with transaction.atomic():
                    process_transaction(
                        request=request,
                        sender=request.user,
                        recipient=new_transaction.recipient.username,
                        amount=new_transaction.amount,
                        currency=new_transaction.currency,
                    )
                messages.success(request, 'Transaction completed successfully.')
                return redirect('home')
            except (OperationalError, ValueError) as e:
                messages.error(request, f"Transaction failed: {e}")
        else:
            messages.error(request, 'Please correct the errors below in the form.')
    else:
        if request.user.is_superuser:
            return redirect('admin:index')
        form = SendMoneyForm(user=request.user)
    return render(request, 'payapp/send_money.html', {'form': form})

@csrf_protect
@login_required
def request_money(request):
    if request.method == 'POST':
        form = RequestMoneyForm(request.POST, user=request.user)
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.sender = request.user  # The user making the request
            new_request.timestamp = get_timestamp()
            new_request.status = 'PENDING'  # Requests start as pending

            # Check if amount is positive
            if new_request.amount <= 0:
                messages.error(request, 'Request failed: Amount must be positive.')
                return render(request, 'payapp/request_money.html', {'form': form})

            # Check if the recipient exists
            try:
                recipient = User.objects.get(username=new_request.recipient)
            except User.DoesNotExist:
                messages.error(request, 'Recipient does not exist.')
                return render(request, 'payapp/request_money.html', {'form': form})

            # Save the request (no balance changes yet for requests)
            try:
                with transaction.atomic():
                    new_request.save()
                    messages.success(request, 'Money request sent successfully!')
                    return redirect('home')  # Redirect to home or another appropriate page
            except OperationalError as e:
                messages.error(request, f"Request failed: {e}")
        else:
            messages.error(request, 'Please correct the errors below in the form.')
    else:
        if request.user.is_superuser:
            return redirect('admin:index')
        form = RequestMoneyForm(user=request.user)

    return render(request, 'payapp/request_money.html', {'form': form})

@login_required
@csrf_protect
def reject_payment_request(request, payment_request_id):
    try:
        with transaction.atomic():
            payment_request = PaymentRequest.objects.get(id=payment_request_id, recipient=request.user,
                                                         status='PENDING')
            payment_request.status = 'REJECTED'
            payment_request.save()
            messages.success(request, "Payment request rejected successfully.")
    except PaymentRequest.DoesNotExist:
        messages.error(request, "Payment request not found or you're not authorized to reject it.")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
    return redirect('home')

@login_required
@csrf_protect
def approve_payment_request(request, payment_request_id):
    try:
        with transaction.atomic():
            # Fetch the payment request that needs to be approved
            payment_request = PaymentRequest.objects.get(
                id=payment_request_id,
                recipient=request.user,
                status='PENDING'
            )

            # Process the transaction between the sender and the recipient
            process_transaction(
                request=request,
                sender=request.user,  # The recipient of the request becomes the sender of the transaction
                recipient=payment_request.sender.username,
                # The sender of the request becomes the recipient of the transaction
                amount=payment_request.amount,
                currency=payment_request.currency,
            )

            # Update the payment request status to 'COMPLETED'
            payment_request.status = 'COMPLETED'
            payment_request.save()

            messages.success(request, "Payment request approved successfully.")
    except PaymentRequest.DoesNotExist:
        messages.error(request, "Payment request not found or you're not authorized to approve it.")
    except ValueError as e:
        messages.error(request, f"Approval failed: {e}")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return redirect('home')
