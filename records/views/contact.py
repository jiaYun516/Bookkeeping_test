from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from records.models import Contact
from records.serializers.contact import *

class ContactCreateView(APIView):
    def get(self, request):
        contacts = Contact.objects.filter(is_deleted=False)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ContactDetailView(APIView):
    def get(self, request, pk):
        contacts = get_object_or_404(Contact, pk=pk, is_deleted=False)
        serializer = ContactSerializer(contacts)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        contacts = get_object_or_404(Contact, pk=pk, is_deleted=False)
        contacts.is_deleted = True
        contacts.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk):
        contacts = get_object_or_404(Contact, pk=pk, is_deleted=False)
        serializer = ContactSerializer(contacts, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    