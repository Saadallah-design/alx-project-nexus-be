from rest_framework import generics, serializers
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


# Now adding functionality of updating or deleting items in the cart

class OrderItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update, or delete a single OrderItem within the active cart.
    """
    serializer_class = OrderItemSerializer
    permission_classes = (IsAuthenticated,)

    # Crucially, we MUST ensure users can only modify items in their own active cart.
    def get_queryset(self):
        # 1. Find the user's active cart to return it and update it
        cart, _ = Order.objects.get_or_create(
            user=self.request.user, 
            status='CART'
        )
        # 2. Return only the OrderItems belonging to that cart
        return OrderItem.objects.filter(order=cart)

    # ensure that quantity cannot drop below 1 during an update.
    def perform_update(self, serializer):
        quantity = serializer.validated_data.get('quantity')
        
        # Prevent setting the quantity to 0 or less via an update
        if quantity is not None and quantity < 1:
            raise serializers.ValidationError({"quantity": "Quantity must be at least 1, or use DELETE to remove the item."})

        serializer.save()