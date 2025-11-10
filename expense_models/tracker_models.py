from django.db import models
import uuid
from expence_tracker import settings

User = settings.AUTH_USER_MODEL

class AccountChoices(models.TextChoices):
    BANK = "BANK", "Bank"
    WALLET = "WALLET", "Wallet"

class Account(models.Model):
    id = models.UUIDField(max_length=30, primary_key=True, default=uuid.uuid4(), unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="accounts")
    name = models.CharField(max_length=250, default="NIgerian_Bank")
    account_type = models.CharField(max_length=200, default=AccountChoices.BANK, choices=AccountChoices)
    balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.user.username} === {self.account_type} === {self.balance}"

    

class Transaction(models.Model):
    id = models.UUIDField(max_length=20, primary_key=True, default=uuid.uuid4(), unique=True)
    name = models.CharField(max_length=200)
    amount = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions")
    user = models.ForeignKey(User, ondelete=models.CASCADE,  related_name="transactions")
    is_income = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    date_of_transaction = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.user.username} === {self.name} === {self.amount}"

