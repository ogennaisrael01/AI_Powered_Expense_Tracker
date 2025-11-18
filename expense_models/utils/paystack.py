import httpx
from expense_tracker import settings
from .retry_on_failures import retry_on_failures
from ..tracker_models import Account, Transaction
from datetime import datetime
from ..utils.email_utils import send_email_notification, withdrawal_email
from django.shortcuts import get_object_or_404
from decimal import Decimal
import uuid

PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
PAYSTACK_URI = settings.PAYSTACK_URI

def initialize_payment(payload: dict):
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    url = f"{PAYSTACK_URI}initialize"
    response = retry_on_failures(httpx.post(url=url, json=payload, headers=headers))
    if not response.get("success"):
        return response.get("message")
    response_data = response.get("request").json()
    if response_data.get("status"):
        return {"success": True, "data": response_data.get("data").get("authorization_url")}

    else:
        return {"success": False, "message": "unable to reach the paystack sservice"}

    
def verify_payments(refrence: str):
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    url = f"{PAYSTACK_URI}verify/{refrence}"
    response = retry_on_failures(httpx.get(url, headers=headers))
    return response.get("request").json()


def initialize_withdrawal(payload: dict):
    request = payload.get("request")
    amount = payload.get("amount")
    account_balance = get_object_or_404(Account, user=request.user)
    if request.user.income < amount or request.user.income < 10:
        return {
            "success": False, 
            "message": f"Insufficient funds. Main balance: {request.user.income}"}

    if isinstance(request.user.income, Decimal):
        request.user.income = float(request.user.income)
    
    request.user.income -= amount
    request.user.save()
    paid_at = datetime.now()
    email = payload.get("customer").get("email")
    refrence = payload.get("refrence")
    currency = payload.get("currency")
    withdrawal_mail = withdrawal_email(
        email=email, 
        refrence=refrence, 
        date=paid_at.strftime("%d %b %Y"), 
        amount=amount, 
        currency=currency
        )

    subject = withdrawal_mail[0]
    body = withdrawal_mail[1]
    try:
        send_notif = send_email_notification(
            subject=subject,
            message=body,
            email="ogennaisrael@gmail.com"
        )
    except Exception as e:
        return {
            "success":False,
            "message": f"Error: {e}"
        }
    # save Trasaction
    transaction = Transaction(
        transaction_id=uuid.uuid4(),
        name="Withdrawal",
        account=account_balance,
        amount=amount,
        transaction_type=Transaction.TransactionType.EXPENSE,
        user=request.user,
        payment_method="BANK",
        date_of_transaction=paid_at.date()

    )
    if transaction:
        transaction.save()
    return {
        "success": True,
        "message": f"{send_notif.get("message")}: Withdrawal completed, reciept sent to email"
    }
