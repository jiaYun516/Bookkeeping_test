from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from records.models import Account
from records.serializers.account import *

class AccountCreateView(APIView):
    def get(self, request):
        accounts = Account.objects.filter(is_deleted=False)
        serializer = AccountSerializer(accounts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AccountSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class AccountDetailView(APIView):
    def get(self, request, pk):
        accounts = get_object_or_404(Account, pk=pk, is_deleted=False)
        serializer = AccountSerializer(accounts)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        accounts = get_object_or_404(Account, pk=pk, is_deleted=False)
        accounts.is_deleted = True
        accounts.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk):
        accounts = get_object_or_404(Account, pk=pk, is_deleted=False)
        serializer = AccountSerializer(accounts, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    