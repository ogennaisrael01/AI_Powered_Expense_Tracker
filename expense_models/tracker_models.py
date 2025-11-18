from django.db import models
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()
print(User)

class Account(models.Model):
    
    account_id = models.UUIDField(
        max_length=30, 
        primary_key=True, 
        default=uuid.uuid4(), 
        unique=True, 
        db_index=True
        )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="accounts")
    name = models.CharField(max_length=250, default="Paystack")
    balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    class Meta:
        ordering = ["-created_at"]
        db_table = "accounts"
        verbose_name = "Account"

    def __str__(self):
        return f"{self.user.username} === {self.name} === {self.balance}"

    

class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        EXPENSE = 'EXPENSE', "Expense"
        INCOME = "INCOME", "Income"

    class PaymentMethod(models.TextChoices):
        CARD = "Card", "card"
        BANK_TRANSFER = "Bank Transfer", "bank_transfer"
        USSD = "USSD", "ussd"
        QR = "QR Payment", "qr "
        BANK = "BANK", "bank"
        MOBILE_MONEY = "MOBILE_MONEY", "mobile_money"

    transaction_id = models.UUIDField(max_length=20, primary_key=True, default=uuid.uuid4(), unique=True, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices, default=TransactionType.EXPENSE)
    user = models.ForeignKey(User, on_delete=models.CASCADE,  related_name="transactions")
    is_income = models.BooleanField(default=False)
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CARD
    )
    description = models.TextField(null=True, blank=True)
    date_of_transaction = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.user.username} === {self.name} === {self.account}"

    class Meta:
        db_table = "transactions"
        ordering = ["-created_at"]
        verbose_name = "Transaction"
