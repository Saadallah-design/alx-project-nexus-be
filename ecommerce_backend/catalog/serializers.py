# Catalog and Product Serializers

from rest_framework import serializers
from .models import Category, Product, ProductImage
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'alt_text', 'order', 'is_primary']
        read_only_fields = ['id']
    
    def get_image_url(self, obj):
        """Return full URL for the image"""
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    # expose the dynamically calculated 'sale_price' property.
    sale_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True) 

    # using nested serializer to expose the category data
    # so instead of just showing the category id, it will show the category name and slug (from the above defined CategorySerializer)
    category = CategorySerializer(read_only=True)
    class Meta:
        model = Product
        fields = (
            'id', 
            'category', 
            'name', 
            'description', 
            'base_price', 
            'sale_price', # This references the method below
            'discount_percentage',
            'images',
            'stock_quantity', 
            'is_available', 
            'is_featured',
            'created_at',
            'updated_at',
        )
        # enhancing security by making the id, created_at, updated_at and sale_price read only
        # so the front end can't modify them 
        read_only_fields = ('id', 'created_at', 'updated_at', 'sale_price')

    # Method to calculate the sale_price for the API output
    def get_sale_price(self, product):
        # We use the @property defined in the Product model
        return product.sale_price


