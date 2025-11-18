from rest_framework import status, permissions
from rest_framework.views import APIView
from .auth_serializers import (
    RegisterSerializer, 
    LoginSerializer, 
    PasswordResetConfirmSerializer, 
    PasswordRestSerializer,
    ProfileViewSerializer,
    ProfileUdateSerializer
)
from .utils.security import encode_payload, decode_payload
from rest_framework.response import Response
from .utils.email_utils import (
    send_email_notification, 
    account_verification_email, 
    reset_password_email, 
    password_reset_successful
)
from expense_tracker.settings import DOMAIN
from django.contrib.auth import get_user_model, authenticate
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
import logging

logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

User = get_user_model()

class RegistrationViewset(APIView):
    http_method_names = ["post"]
    authentication_classes = []
    permission_classes = []
    serializer_class = RegisterSerializer


    def post(self, request, *args, **kwargs):
        serializer  = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)       
        user = serializer.save()
        sub = {
            "email": user.email,
            "id": str(user.id)
        }
        try:
            token = encode_payload(sub)
        except Exception as e:
            return Response({
                "success": False,
                "message": f"error generating token {e}"
            })
        username = user.username
        verification_link = f"{DOMAIN}/api/v1/verify?token={token}"
        verification_email = account_verification_email(user=username, link=verification_link)
        subject = verification_email[0]
        body = verification_email[1]

        if subject and body:
            try:
                send_notif = send_email_notification(
                    subject=subject,
                    message=body,
                    email=user.email
                )
                if send_notif.get("success"):
                    return Response(
                        {
                            "success": True,
                            "message": f'Account Resgistration Successfull \n {send_notif.get("message")}'
                        },
                        status=201
                    )
            except Exception as e:
                return Response({
                    "success": False,
                    "message": send_notif.get("message")
                })
        
    
class LoginView(APIView):
    permission_classes = []
    http_method_names = ["post"]
    authentication_classes = []
    serializer_class =  LoginSerializer



    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")
        try:
            user = authenticate(request, username=email, password=password)
            if not user:
                return Response({
                    "success": False,
                    "message": "invalid credentails"
                }, status=status.HTTP_400_BAD_REQUEST)
            if user and not user.is_verified:
                return Response({"success": False,"message": "unverified account, please verify your account!"})                
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "success": True,
                "user_id": user.id,
                "token": token.key
            }, status=200)
        except Exception as e:
            return Response({
                "success": False,
                "message": f"Error: {e}"
            }, status=400)

class VerifyAccountView(APIView):
    http_method_names = ["put"]
    authentication_classes = []
    permission_classes = []

    def put(self, request, *args, **kwargs):
        token = request.query_params.get("token")
        if not token:
            return Response({"success": False, "message": "provide the token"}, status=status.HTTP_400_BAD_REQUEST)
        payload = decode_payload(token)
        email = payload.get("email")
        id = payload.get("id")
        if not email and id is None:
            return Response("cant verify without user credentials")
        user = User.objects.get(id=id, email=email)
        if user.is_verified:
            return Response("has been verified")

        user.is_verified = True
        user.save()
        return Response({
            "success": True,
            "message": "verification Successfull"
        })

class RequestPasswordResetView(APIView):
    http_method_names = ["post"]
    authentication_classes = []
    permission_classes = []
    serializer_class = PasswordRestSerializer


    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        if not email:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                "message": "please  provide your email address"
            })
        user = get_object_or_404(User, email=email)
        sub = {
            "email": user.email,
            "id": str(user.id)
        }

        token = encode_payload(sub)
        if not token:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                "message": "unable to generate token"
            })
        
        link = f"{DOMAIN}/api/v1/password/reset-confirm?token={token}"

        send_reset_email = reset_password_email(user=user.username, link=link)
        subject = send_reset_email[0]
        body = send_reset_email[1]
        try:
            if subject and body:
                send_notif = send_email_notification(
                    subject=subject,
                    message=body,
                    email=user.email
                )
                if send_notif.get("success"):
                    return Response(status=status.HTTP_200_OK, data={
                        "success": True,
                        "message": f"reset passwod {send_notif.get("message")}"
                    })
                return Response(data="error occured")
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=e)


class PasswordResetConfirmView(APIView):
    http_method_names = ["put"]
    authentication_classes = []
    permission_classes = []
    serializer_class = PasswordResetConfirmSerializer

    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = request.query_params.get("token")
        if not token:
            return False
        sub: dict = decode_payload(token)
        email = sub.get("email")
        id = sub.get("id")
        user = get_object_or_404(User, pk=id)
        password = serializer.validated_data.get("password")
        user.set_password(password)
        user.save()
        try :
            confirm_email = password_reset_successful(user=user.username)
            send_notif = send_email_notification(
                    subject=confirm_email[0],
                    message=confirm_email[1],
                    email=user.email
            )
            if send_notif.get("success"):
                logging.info(send_notif.get("message"))
            else:
                logging.error(send_notif.get("message"))
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                "message": f"Error: {e}"
            })
        return Response(status=status.HTTP_200_OK, data={
            "success": True,
            "message": "account reset successful"
        })


class ProfileView(APIView):
    http_method_names = ["get", "put"]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileViewSerializer

    def get(self, request, *args, **kwargs):
        user_email = request.user.email
        profile_object = get_object_or_404(User, email=user_email)
        serializer = self.serializer_class(profile_object)
        return Response(status=status.HTTP_200_OK, data={"success": True, "data": serializer.data})

    def put(self, request, *args, **kwargs):
        user_object = get_object_or_404(User, id=request.user.id)
        serializer = ProfileUdateSerializer(user_object, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK, data={"success": True, "updated data": serializer.data})