from rest_framework import serializers
from .tracker_models import Account, Transaction

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "user", "account_type", "balance", "name", "created_at", "updated_at"]
        read_only_fields = ["user", "id", "created_at", "updated_at", "balance"]

        
class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    class Meta: 
        model = Transaction
        fields = ["id", "user", "accounts", "name", "is_income", "date_of_transaction", "created_at"]