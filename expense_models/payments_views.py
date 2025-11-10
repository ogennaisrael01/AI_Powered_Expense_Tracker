from rest_framework.views import APIView
from .utils.paystack import initialize_payment, verify_payments
from .tracker_serializers import DepositSerializer
import uuid
from rest_framework import permissions, status
from expence_tracker import settings
from rest_framework.response import Response
from decimal import Decimal

DOMAIN = settings.DOMAIN

def generate_refrence():
    return f"refetx_{uuid.uuid4().hex[:10]}"

class DepositView(APIView):
    http_method_names = ["post"]
    permission_classes = []
    serializer_class = DepositSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data.get("amount") * 100
        if isinstance(amount, Decimal):
            amount = float(amount)
        payload = {
            "email": request.user.email,
            "amount": amount,
            "currency": "NGN",
            "channels": ["card", "bank_transfer", "bank", "ussd", "qr", "mobile_money"],
            "reference": generate_refrence(),
            "callback_url": f"{DOMAIN}api/v1/verify/payment",
        }

        checkout = initialize_payment(payload)
        if checkout.get("success"):
            return Response(status=status.HTTP_200_OK,  data= {"succcess": True, "checkout_url": checkout.get("data")})
        return Response(status=status.HTTP_502_BAD_GATEWAY, data={
            "success": False,
            "message": checkout.get("message")
        })

class VerifyView(APIView):
    http_method_names = ["get"]
    permission_classes = []

    def get(self, request, *args, **kwargs):
        refrence = request.query_params.get("refrence")
        if not refrence:
            return False
        verify = verify_payments(refrence)
        if verify.get("data").get("status") == "success":
            ...