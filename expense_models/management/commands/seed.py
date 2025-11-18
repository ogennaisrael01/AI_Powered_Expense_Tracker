from django.core.management.base import BaseCommand
from faker import Faker
from django.contrib.auth import get_user_model
from expense_models.tracker_models import Account, Transaction
import json
from decimal import Decimal
import uuid
import random

User = get_user_model()

class Command(BaseCommand):
    help = "Populating db with testing data"


    def handle(self, *args, **options):    
        faker = Faker()

        # Free up database tables 
        User.objects.all().delete()
        Account.objects.all().delete()
        Transaction.objects.all().delete()

        
        NUM_USERS = 2_000
        for i in range(NUM_USERS):
            self.stdout.write(f"SEEDING {i+1}....")
            password = faker.password(length=12)
            email = faker.email()
            if User.objects.filter(email=email).exists():
                self.stdout.write(f"{email} already exists in the db")
                continue
            users = User.objects.create_user(
                email=email,
                username=faker.user_name(),
                password=password,
                first_name=faker.first_name(),
                last_name=faker.last_name()
            )
            data = {
                "email": email,
                "password": password
            }
            with open("users_data.json", "+a") as f:
                json.dump(data, f, indent=4)

        self.stdout.write("SEEDED USERS DATA")
        users = User.objects.all()
        BATCHES = 400
        ACCOUNT_DATA = []
        for user in users:
            """ Creating account for each user in our database"""
            self.stdout.write("SEEDING ACCOUNT DATA")
            account = Account(
                account_id=uuid.uuid4(),
                user=user,
                name=faker.text()[:20],
                balance=Decimal(faker.random_number(digits=5, fix_len=True))
            )
            ACCOUNT_DATA.append(account)

            if len(ACCOUNT_DATA) == BATCHES:
                self.stdout.write(f"SEEDING {len(ACCOUNT_DATA)} ACCOUNT DATA ...")
                Account.objects.bulk_create(ACCOUNT_DATA)
                ACCOUNT_DATA.clear()
        if len(ACCOUNT_DATA) > 0:
            self.stdout.write(f"SEEDING {len(ACCOUNT_DATA)} ACCOUNT DATA ...")
            Account.objects.bulk_create(ACCOUNT_DATA) 
            ACCOUNT_DATA.clear()
        self.stdout.write("SEEDED ACCOUNT DATA")

        
        accounts = Account.objects.all()
        BATCHES = 1_000
        TOTAL_NUM = 5_000
        TRANSACTION_DATA = []
        transaction_type = ["INCOME", "EXPENSE"]
        payment_method = ["CARD", "BANK_TRANSFER", "USSD", "QR", "BANK", "MOBILE_MONEY"]
        for i in range(TOTAL_NUM):
            self.stdout.write(F"SEEDING {i+1} DATA")
            try:
                transaction = Transaction(
                    transaction_id=uuid.uuid4(),
                    name=faker.text()[:20],
                    account=random.choice(accounts),
                    user=random.choice(users),
                    amount=faker.random_number(digits=4),
                    transaction_type=random.choice(transaction_type),
                    is_income=faker.boolean(chance_of_getting_true=50),
                    payment_method=random.choice(payment_method),
                    description=faker.text(),
                    date_of_transaction=faker.date(),

                )
            except Exception as e:
                raise Exception
            
            TRANSACTION_DATA.append(transaction)

        
            if len(TRANSACTION_DATA) == BATCHES:
                self.stdout.write(f"SEEDING {len(TRANSACTION_DATA)} ACCOUNT DATA ...")
                Transaction.objects.bulk_create(TRANSACTION_DATA)
                TRANSACTION_DATA.clear()
        if len(TRANSACTION_DATA) > 0:
            self.stdout.write(f"SEEDING {len(TRANSACTION_DATA)} ACCOUNT DATA ...")
            Transaction.objects.bulk_create(TRANSACTION_DATA) 
            TRANSACTION_DATA.clear()
        self.stdout.write("SEEDED Transaction DATA")

