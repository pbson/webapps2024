from rest_framework.views import APIView
from rest_framework.response import Response
from conversion.serializers import CurrencyConversionSerializer

# Currency conversion rates
CONVERSION_RATES = {
    'GBP': {
        'USD': 1.3,
        'EUR': 1.1,
    },
    'USD': {
        'GBP': 0.77,
        'EUR': 0.9,
    },
    'EUR': {
        'GBP': 0.85,
        'USD': 1.11,
    },
}


def convert_currency(base_currency, target_currency, amount):
    # Check if the base and target currencies are the same
    if base_currency == target_currency:
        return amount

    rate = CONVERSION_RATES.get(base_currency, {}).get(target_currency)

    if rate is None:
        return None

    return amount * rate


class ConvertCurrency(APIView):
    def get(self, request, base_currency, target_currency, amount):
        # Validate currencies
        valid_currencies = {'USD', 'EUR', 'GBP'}
        if base_currency.upper() not in valid_currencies or target_currency.upper() not in valid_currencies:
            return Response({'error': 'Unsupported currency code.'}, status=400)

        # Validate and convert amount
        try:
            amount = float(amount)
        except ValueError:
            return Response({'error': 'Invalid amount format.'}, status=400)

        # Convert the currency
        converted_amount = convert_currency(base_currency.upper(), target_currency.upper(), amount)
        # Check if conversion was successful
        if converted_amount is None:
            return Response({'error': 'Conversion rate not available.'}, status=400)

        # Serialize the response data
        data = {
            'base_currency': base_currency,
            'target_currency': target_currency,
            'amount': round(amount, 10),
            'converted_amount': round(converted_amount, 10),
        }
        serializer = CurrencyConversionSerializer(data=data)
        if serializer.is_valid():
            print(serializer.data)
            return Response(serializer.data)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=400)
