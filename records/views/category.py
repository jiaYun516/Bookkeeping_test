from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from records.models import Category
from records.serializers.category import *

class CategoryCreateView(APIView):
    def get(self, request):
        categories = Category.objects.filter(is_deleted=False)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CategoryDetailView(APIView):
    def get(self, request, pk):
        categories = get_object_or_404(Category, pk=pk, is_deleted=False)
        serializer = CategorySerializer(categories)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        categories = get_object_or_404(Category, pk=pk, is_deleted=False)
        categories.is_deleted = True
        categories.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk):
        category = get_object_or_404(Category, pk=pk, is_deleted=False)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    