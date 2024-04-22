from rest_framework import serializers


class CurrencyConversionSerializer(serializers.Serializer):
    base_currency = serializers.CharField(max_length=3)
    target_currency = serializers.CharField(max_length=3)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    converted_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
