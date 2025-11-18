from rest_framework import serializers
from .tracker_models import Account, Transaction


class AccountCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)

    def validate_name(self, value):
        if len(value) < 5:
            raise serializers.ValidationError(f"provide a more detailed name, {len(value)} characters is too short")
        return value
    
    def create(self, validated_data):
        account = Account.objects.create(**validated_data)
        return account
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.save()
        return instance

        
class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class TransactionSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Transaction
        fields = ["transaction_id", "name", "amount", "transaction_type", "is_income", "date_of_transaction", "created_at", "payment_method", "description"]
        read_only_fileds = ["transaction_id", "created_at", ]


class WithDrawSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2) 
    currency = serializers.ChoiceField(choices=["NGN", "USD"])
    account_number = serializers.CharField(max_length=10)

    def validate_account_number(self, value: str):
        if not value.isdigit() or len(value)  > 10:
            raise serializers.ValidationError(f"Invalid account number: {value}")
        return value


class AccountSerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True)
    user = serializers.ReadOnlyField(source="user.username")
    class Meta:
        model = Account
        fields = ["account_id", "user", "balance", "name", "created_at", "transactions"]
        read_only_fields = ["user", "id", "created_at", "updated_at", "balance", "transactions"]
