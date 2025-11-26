from rest_framework import generics
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

# using pre-defined views from rest_framework

class CategoryListView(generics.ListAPIView):
    """API endpoint to list all product categories."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductListCreateView(generics.ListCreateAPIView):
    """API endpoint to list and create products."""
    serializer_class = ProductSerializer

    def get_queryset(self):
        """
        Filter products by availability and optionally by category.
        Query params: ?category=<slug>
        """
        # Start with only available products
        queryset = Product.objects.filter(is_available=True)
        
        # Optionally filter by category slug
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        return queryset

