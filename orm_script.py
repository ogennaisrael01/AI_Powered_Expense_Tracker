import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expense_tracker.settings')
django.setup()

from django.contrib.auth import get_user_model
from expense_models.tracker_models import Transaction, Account

User = get_user_model()

def run():
    user = User.objects.filter(username='gdodson').first()
    transaction = user.transactions.all()
    tra = transaction.filter(name="Deposit")
    print(transaction)
    print(tra)

if __name__ == "__main__":
    run()
