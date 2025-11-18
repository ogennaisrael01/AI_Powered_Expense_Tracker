from rest_framework.views import APIView
from .utils.paystack import initialize_payment, verify_payments, initialize_withdrawal
from .tracker_serializers import DepositSerializer, WithDrawSerializer
import uuid
from rest_framework import permissions, status
from expense_tracker import settings
from rest_framework.response import Response
from decimal import Decimal
from django.shortcuts import get_object_or_404
from .tracker_models import Account, Transaction
from datetime import datetime

DOMAIN = settings.DOMAIN

def generate_refrence():
    return f"refetx_{uuid.uuid4().hex[:10]}"

class DepositView(APIView):
    http_method_names = ["post"]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DepositSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data.get("amount") * 100
        if isinstance(amount, Decimal):
            amount = float(amount)
        refrence = generate_refrence()
        payload = {
            "email": request.user.email,
            "amount": amount,
            "currency": "NGN",
            "channels": ["card", "bank_transfer", "bank", "ussd", "qr", "mobile_money"],
            "reference": refrence,
            "callback_url": f"{DOMAIN}api/v1/verify/payment?refrence={refrence}",
        }

        checkout = initialize_payment(payload)
        if checkout.get("success"):
            return Response(status=status.HTTP_200_OK,  data= {"succcess": True, "checkout_url": checkout.get("data")})
        return Response(status=status.HTTP_502_BAD_GATEWAY, data={
            "success": False,
            "message": checkout.get("message")
        })


class VerifyView(APIView):
    http_method_names = ["post"]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refrence = request.query_params.get("refrence")
        if not refrence:
            return False
        try:
            verify_payment = verify_payments(refrence)
        except Exception as e:
            return Response(status=status.HTTP_502_BAD_GATEWAY, data=e)
        if verify_payment.get("status") and verify_payment["data"]["customer"]["email"] == request.user.email:
            """ update user income and accoiunt balance, updating the transaction as well"""
            amount = verify_payment.get("data").get("amount") / 100
            request.user.income += Decimal(amount)
            request.user.save() # save user income

            # acount balance update
            user_account = get_object_or_404(Account, user=request.user) 

            # Transaction update
            payment_method = verify_payment.get("data").get("channel")
            paid_at = verify_payment.get("data").get("paid_at")
            date_obj = datetime.strptime(paid_at, "%Y-%m-%dT%H:%M:%S.%fZ")
            transaction = Transaction(
                user=request.user,
                name="Deposit",
                account=user_account,
                amount=amount,
                transaction_type=Transaction.TransactionType.INCOME,
                is_income=True,
                payment_method=payment_method.upper(),
                description=verify_payment.get("data").get("message"),
                date_of_transaction=date_obj.date()
                
            )
        if transaction:
            transaction.save()

            return Response(status=status.HTTP_200_OK, data={"success": True, "message": "Payment verified , account updated"})
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"success": False, "message": "Failed to verify"})


class WithDrawView(APIView):
    http_method_names = ["post"]
    serializer_class = WithDrawSerializer
    permission_classes = [permissions.IsAuthenticated]


    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data.get("amount")
        if isinstance(amount, Decimal):
            amount = float(amount)

        payload = {
            "request": request,
            "id": uuid.uuid4(),
            "amount":amount,
            "bank": serializer.validated_data.get("bank_name"),
            "currency": serializer.validated_data.get("currency"),
            "refrence": generate_refrence(),
            "customer": {
                "email": request.user.email,

            }
        }
        verify_withdrawals = initialize_withdrawal(payload)
        if verify_withdrawals.get("success"):
            return Response(status=status.HTTP_200_OK, data={"success":True, "message": verify_withdrawals.get("message")})
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"success": False, "message": verify_withdrawals.get("message")})

        
            
         