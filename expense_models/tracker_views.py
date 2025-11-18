from rest_framework import status, permissions
from rest_framework.response import Response
from .tracker_serializers import AccountSerializer, AccountCreateSerializer, TransactionSerializer
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from .tracker_models import Account, Transaction
from rest_framework.pagination import PageNumberPagination
from decimal import Decimal


class AccountPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = page_size
    max_page_size = 50



class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountCreateSerializer
    queryset = Account.objects.all()
    pagination_class = AccountPagination
    permission_classes = [permissions.IsAuthenticated]
    

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        # Admin users can view all account. Quest users can view only thier account
        queryset = self.get_queryset()
        if request.user.is_superuser:
            queryset = queryset
        else:
            queryset = queryset.filter(user=request.user)
        serializer = AccountSerializer(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data={"success": True, "data": serializer.data})
    
    def update(self, request, *args, **kwargs):
        account = self.get_object()
        serializer = self.get_serializer(account, data=request.data)
        serializer.is_valid(raise_exception=True)
        if account.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN, data={"success": False, "data": "You are not authorised to perform this action"})
        
        serializer.save(user=request.user)
        return Response(status=status.HTTP_201_CREATED, data={"success": True, "message": "updated account" })
    
    def destroy(self, request, *args, **kwargs):
        account = self.get_object()
        if account.user == request.user or request.user.is_superuser:
            account.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_403_FORBIDDEN, data={"success": False, "message": "Can't perform this action"})

        
    
    def retrieve(self, request, *args, **kwargs):
        account = self.get_object()
        if account.user == request.user or request.user.is_superuser:
            serializer = AccountSerializer(account)
            return Response(serializer.data)
        return Response("can't perform this action")



class TransactionViewSet(viewsets.ModelViewSet):
    """ Track your Expenses in one Piece """

    serializer_class = TransactionSerializer
    queryset = Transaction.objects.select_related("account")
    pagination_class = AccountPagination
    permission_classes = [permissions.IsAuthenticated]


    def perform_create(self, serializer):
        transaction_type = serializer.validated_data.get("transaction_type")
        amount = serializer.validated_data.get("amount")
        account_income = get_object_or_404(Account, user=self.request.user)
        if isinstance(amount, Decimal):
            amount = float(amount)

        if isinstance(account_income.balance, Decimal):
            account_income.balance = float(account_income.balance)
        if account_income.balance is None:
            account_income.balance = 0

        if transaction_type == Transaction.TransactionType.INCOME:
            serializer.validated_data["is_income"] = True
            account_income.balance += amount
            account_income.save()

        else:

            account_income.balance -= amount
            account_income.save()    
        serializer.save(user=self.request.user, account=account_income)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(status=status.HTTP_201_CREATED, data={"success": True, "data": serializer.validated_data})

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if request.user.is_superuser:
            queryset = queryset
        else:
            queryset = queryset.filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        transaction = self.get_object()
        if request.user != transaction.user:
            return Response(status=status.HTTP_403_FORBIDDEN, data={"success": True, "message": "Can't perform this action"})
        transaction.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def update(self, request, *args, **kwargs):
        transaction = self.get_object()
        if transaction.user == request.user:
            serializer = self.get_serializer(transaction, data=reqeust.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(seriaizer)
            return Response(status=status.HTTP_200_OK, data={"success": True, "data": serializer.validated_data})
        return Response(status=status.HTTP_403_FORBIDDEN, data={"success": False, "message": "Can't perform this action"})
    
    def retrieve(self, request, *args, **kwargs):
        transaction = self.get_object()
        if request.user == transaction.user or request.user.is_superuser:
            serializer = self.get_serializer(transaction, many=True)
            return Response(serializer.data)
        return Response(status=status.HTTP_403_FORBIDDEN, data={"success": False, "message": "Can't perform this action"})
    
    def partial_update(self, request, *args, **kwargs):
        transaction = self.get_object()
        serializer = self.get_serializer(transaction, data=request.data, partial=True)
        if transaction.user == reqeust.request:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(status=status.HTTP_200_OK, data={"success": True, "data": serializer.validated_data})
        return Response(status=status.HTTP_403_FORBIDDEN, data={"success": False, "message": "Can't perform this action"})
    




