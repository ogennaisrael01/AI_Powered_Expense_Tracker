from rest_framework import status, permissions
from rest_framework.response import Response
from .tracker_serializers import AccountSerializer
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .tracker_models import Account


class AccountView(APIView):
    http_method_names = ["post", "get"]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AccountSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        accounts = get_object_or_404(Account, user=user)
        serializer = self.serializer_class(accounts)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        account_type = serializer.validated_data.get("account_type")
        if Account.objects.filter(user=request.user, account_type=account_type).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"success": False, "message": "You already have this account type"})
        serializer.save(user=request.user)  
        return Response(serializer.data)
    
class AccountRetreiveView(APIView):
    http_method_names = ["get", "put", "delete"]
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id, format=None):
        user = request.user
        account = get_object_or_404(Account, id=id, user=user)
        if not account:
            return Response("No active accout found")
        serializer = self.serializer_class(account)
        return Response(serializer.data)
    
    def put(self, request, id, format=None):
        user = request.user
        account_object = get_object_or_404(Account, id=id, user=user)
        serializer = self.serializer_class(account_object, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def delete(self, request, id, format=None):
        user = request.user
        account = get_object_or_404(Account, id=id, user=user)
        account.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



