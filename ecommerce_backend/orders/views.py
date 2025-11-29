from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from .models import Order, OrderItem
from .serializers import CartSerializer, OrderItemSerializer, CheckoutSerializer
from rest_framework.response import Response


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

# Checkout View using generics.GenericAPIView

class CheckoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CheckoutSerializer
    
    def post(self, request):
        # 1. Get user's active cart
        try:
            # again using the user=request.user to ensure the cart belongs to the user asking for it 
            cart = Order.objects.get(user=request.user, status='CART')
        except Order.DoesNotExist:
            # if no active cart is found, return a 400 Bad Request response
            # to be edited lated to me more human readable error messages
            return Response(
                {"error": "No active cart found"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. Validate cart has items
        if not cart.items.exists():
            return Response(
                {"error": "Cart is empty"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 3. Save shipping info
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # using get() just for extar safety 
        # normally since first 3 fields are required, they should always be present but just adding a layer of safety
        cart.shipping_address = serializer.validated_data.get('shipping_address')
        cart.shipping_city = serializer.validated_data.get('shipping_city')
        cart.shipping_postal_code = serializer.validated_data.get('shipping_postal_code')
        cart.shipping_country = serializer.validated_data.get('shipping_country', 'Morocco')
        
        # 4. Change status to PENDING
        cart.status = 'PENDING'
        cart.save()
        
        # 5. Return order for payment
        return Response({
            "message": "Order placed. Proceed to payment.",
            "order_id": str(cart.id),
            "total": float(cart.total_price)
        })