from rest_framework import serializers
from drf_writable_nested.serializers import WritableNestedModelSerializer
from django.db import transaction as db_transaction
from decimal import Decimal

from records.models import Transaction, TransactionItem, Contact
from records.signals import apply_transaction_impact

class TransactionItemSerializer(serializers.ModelSerializer):
    contact = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.all(),
        required=False,
        default=lambda: Contact.objects.get(id=1)
    )

    class Meta:
        model = TransactionItem
        fields = ['id', 'amount', 'selling_amount', 'category', 'contact', 'status', 'tag']
    
    def validate_contact(self, value):
        if value is None:
            return Contact.objects.get(id=1)
        return value

class TransactionSerializer(serializers.ModelSerializer):
    items = TransactionItemSerializer(many=True, required=False)
    class Meta:
        model = Transaction
        fields = ['id', 'transaction_type', 'account', 'to_account', 'total_amount', 'items', 'note']


    def validate(self, data):
        """
        全域事件：跨資料表的總額對帳檢查
        """
        # 1. 取得這次請求傳進來的 total_amount 與 items
        total_amount = data.get('total_amount', getattr(self.instance, 'total_amount', None))
        items_data = data.get('items', None)

        # 情況 A：本次請求有傳入 items (POST / PUT / 包含 items 的 PATCH)
        if items_data is not None:
            items_sum = sum(Decimal(str(item.get('amount', 0))) for item in items_data)
            if total_amount is not None and Decimal(str(total_amount)) != items_sum:
                raise serializers.ValidationError({
                    "total_amount": f"總金額 ({total_amount}) 與明細金額總和 ({items_sum}) 不符！"
                })

        # 情況 B：PATCH 請求只改了 total_amount，沒有傳 items (要拿 DB 既有的舊明細來比對)
        elif self.instance and 'total_amount' in data and items_data is None:
            db_items = self.instance.items.all()
            items_sum = sum(Decimal(str(item.amount)) for item in db_items)
            if Decimal(str(total_amount)) != items_sum:
                raise serializers.ValidationError({
                    "total_amount": f"更新的總金額 ({total_amount}) 與資料庫現有明細總和 ({items_sum}) 不符！"
                })

        return data

    def create(self, validated_data):
        with db_transaction.atomic():
            items_data = validated_data.pop('items', [])
            transaction_obj = Transaction.objects.create(**validated_data)

            default_contact = Contact.objects.get(id=1)
            for item_data in items_data:
                if not item_data.get('contact'):
                    item_data['contact'] = default_contact
                TransactionItem.objects.create(transaction=transaction_obj, **item_data)

            # 明細與主單建立完畢，觸發平帳 (套用)
            apply_transaction_impact(transaction_obj=transaction_obj, action="apply")

        return transaction_obj

    def update(self, instance, validated_data):
        with db_transaction.atomic():
            # 1. 撤銷舊影響 (此時舊明細還完好地位於 DB 中)
            apply_transaction_impact(transaction_obj=instance, action="revert")

            # 2. 更新主單資料
            items_data = validated_data.pop('items', None)
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            # 3. 若有傳入新明細，清空舊明細並重建
            if items_data is not None:
                instance.items.all().delete()
                default_contact = Contact.objects.get(id=1)
                for item_data in items_data:
                    if not item_data.get('contact'):
                        item_data['contact'] = default_contact
                    TransactionItem.objects.create(transaction=instance, **item_data)

            # 4. 對更新後的交易套用新影響
            apply_transaction_impact(transaction_obj=instance, action="apply")

        return instance
