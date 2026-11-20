from rest_framework import serializers
from records.models import Contact

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'group_name', 'balance', 'is_active', 'note']
        read_only_fields = ['balance']