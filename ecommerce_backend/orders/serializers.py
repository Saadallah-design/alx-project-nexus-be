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
