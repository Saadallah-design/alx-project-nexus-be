from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Order, OrderItem
from .serializers import CartSerializer, OrderItemSerializer


# Cart Retrieve View
class CartRetrieveView(generics.RetrieveAPIView):
    """API endpoint for retrieving the current user's active cart."""
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # checking first if the user has an active cart
        user = self.request.user
        # tries to find an active cart for the user with status 'CART'
        # if it doesn't exist, it creates one
        cart, created = Order.objects.get_or_create(
            user=user,
            status='CART'
        )
        return cart


# the order item manage view handles add to cart logic, and update quantity logic and locking price
class OrderItemManageView(generics.ListCreateAPIView):
    """API endpoint for managing order items in the cart."""
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Security: Only allow managing items in the user's own active cart
        cart, _ = Order.objects.get_or_create(
            user=self.request.user,
            status='CART'
        )
        # return all the items in the cart
        return OrderItem.objects.filter(order=cart)

    def perform_create(self, serializer):
        # security check
        user = self.request.user
        quantity = serializer.validated_data.get('quantity', 1)
        product = serializer.context['product'] # prefetched product obj since I stored it in the context

        # step 1: get or create the user's active cart
        cart, _ = Order.objects.get_or_create(user = user,status='CART')

        # step 2: check if the product is already in the cart
        
        try:
            order_item = OrderItem.objects.get(order=cart, product=product)
            order_item.quantity += quantity # if it exist update
            order_item.save() # then save
            serializer.instance = order_item

        except OrderItem.DoesNotExist:
            # if not exist create it
            serializer.save(order=cart, product=product, price=product.sale_price)