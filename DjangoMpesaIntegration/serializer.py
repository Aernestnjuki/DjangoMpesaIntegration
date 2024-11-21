from .validators import validate_possible_number
from .models import Transaction

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

class MpesaCheckoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'phone_number',
            'amount',
            'reference',
            'description'
        ]

    def validate_phone_number(self, phone_number):
        """Removing the preciding + or replacing the 0 with 254"""
        if phone_number[0] == '+':
            phone_number = phone_number[1:]
        if phone_number[0] == '0':
            phone_number = '254' + phone_number[1:]

        try:
            validate_possible_number(phone_number, 'KE')
        except:
            raise serializers.ValidationError({'error': 'Phone number is not valid'})
        
        return phone_number
    
    def validate_amount(self, amount):
        """Accepting amounts greater than 0"""
        if not amount or float(amount) <= 0:
            raise serializers.ValidationError(
                {'error': 'Amount must be greater than Zero'}
            )
        return amount
    
    def validate_reference(self, reference):
        if reference:
            return reference
        return "Test"
    
    def validate_description(self, description):
        if description:
            return description
        return "Test"
    

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"