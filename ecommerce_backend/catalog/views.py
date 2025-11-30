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
        Optimized product listing with indexes and query optimization.
        Filter products by availability and optionally by category.
        Query params: ?category=<slug>
        """
        # Optimized query: uses indexes and reduces N+1 queries
        queryset = Product.objects.select_related(
            'category'  # Fetch category in same query (avoid N+1)
        ).prefetch_related(
            'images'  # Prefetch product images
        ).filter(
            is_available=True  # Uses product_avail_date_idx or product_cat_avail_idx
        )
        
        # Optionally filter by category slug
        category_slug = self.request.query_params.get('category')
        if category_slug:
            # Uses product_cat_avail_idx composite index
            queryset = queryset.filter(category__slug=category_slug)
        
        # Default ordering uses product_avail_date_idx
        return queryset

class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint to retrieve, update, or delete a specific product."""
    serializer_class = ProductSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        """Optimized single product query with related data."""
        return Product.objects.select_related(
            'category'
        ).prefetch_related(
            'images'
        )

class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint to retrieve, update, or delete a specific category."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # instead of using uuid pk I will be using the lookup_field
    lookup_field = 'slug'