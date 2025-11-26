from django.shortcuts import render
from rest_framework import generics
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

# using pre-defined views from rest_framework

class CategoryListView(generics.ListAPIView):
    #API endpoint to list all product categories.
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductListCreateView(generics.ListCreateAPIView):
    #API endpoint to list and create products.
    # queryset = Product.objects.all()
    # instead of listing all products I will list only those that are available
    queryset = Product.objects.filter(is_available=True)
    serializer_class = ProductSerializer