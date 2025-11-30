# creating cart endpoints to make the order process accessible to the user

from rest_framework import serializers
from .models import Order, OrderItem
from catalog.models import Product


# OrderItemSerializer is for input and involves server side logic (for validation and price locking)
class OrderItemSerializer(serializers.ModelSerializer):
    # product_id is write_only because it is not needed in the response
    product_id = serializers.UUIDField(write_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        # "order" field is ommited from the serializer 
        fields = ['id', 'product_id', 'product_name', 'quantity', 'price', 'extended_price']
        read_only_fields = ['price', 'extended_price']

        # now this orderItemSerializer is used in the CartSerializer. 
        # it needs a validation method to ensure the product_id is valid
    def validate_product_id(self, product_id):
        try:
            # first let's check if the product exists in our database
            product = Product.objects.get(id=product_id)
            if not product.is_available:
                raise serializers.ValidationError("This product is currently not available")
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")

        # store the product in the serializer context for later use
        # trying to use database queries as little as possible
        self.context['product'] = product
        return product_id


# CartSerializer is for output and involves server side logic (for total price calculation)
class CartSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'status','items', 'total_price','created_at' ]
        read_only_fields = ['status','total_price','created_at']

# Checkout flow serializer
class CheckoutSerializer(serializers.Serializer):
    # Contact Information
    first_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    last_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    phone_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    
    # Address Information
    shipping_address = serializers.CharField(required=True)
    shipping_address_line_2 = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    shipping_city = serializers.CharField(required=True)
    shipping_state = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    shipping_postal_code = serializers.CharField(required=True)
    shipping_country = serializers.CharField(default='Morocco')


# Order Detail Serializer for order history
class OrderDetailSerializer(serializers.ModelSerializer):
    """Detailed order information for order history"""
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'status', 'items', 'total_price',
            'first_name', 'last_name', 'phone_number', 'email',
            'shipping_address', 'shipping_address_line_2',
            'shipping_city', 'shipping_state', 
            'shipping_postal_code', 'shipping_country',
            'payment_method', 'paid_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_price', 'created_at', 'updated_at']


# Guest Checkout Serializer
class GuestCheckoutSerializer(CheckoutSerializer):
    """Guest checkout requires email"""
    email = serializers.EmailField(required=True)  # Override to make required
    
    def validate_email(self, value):
        # Basic email validation
        if not value or '@' not in value:
            raise serializers.ValidationError("Valid email is required for guest checkout")
        return value.lower()


# Guest Order Lookup Serializer
class GuestOrderLookupSerializer(serializers.Serializer):
    """Lookup guest order by email and order ID"""
    email = serializers.EmailField(required=True)
    order_id = serializers.UUIDField(required=True)