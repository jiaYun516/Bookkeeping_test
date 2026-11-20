from rest_framework import serializers
from records.models import Account

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'name', 'account_type', 'balance', 'is_active', 'note']
        read_only_fields = ['balance']