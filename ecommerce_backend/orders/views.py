from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Order, OrderItem
from .serializers import (CartSerializer, OrderItemSerializer, CheckoutSerializer, 
                          OrderDetailSerializer, GuestCheckoutSerializer, GuestOrderLookupSerializer)
from rest_framework.response import Response
from django.utils import timezone # for the payment view
from .tasks import send_order_confirmation_email  # Celery task


# Cart Retrieve View
class CartRetrieveView(generics.RetrieveAPIView):
    """API endpoint for retrieving the current user's active cart (supports guests)."""
    serializer_class = CartSerializer
    permission_classes = [AllowAny]  # Allow guests

    def get_object(self):
        if self.request.user.is_authenticated:
            # Optimized: uses order_user_status_idx index
            cart, created = Order.objects.select_related(
                'user'
            ).prefetch_related(
                'items__product__category',
                'items__product__images'
            ).get_or_create(
                user=self.request.user,
                status='CART'
            )
        else:
            # Optimized: uses order_guest_cart_idx index
            # Guest user - session-based cart
            session_key = self.request.session.session_key
            if not session_key:
                self.request.session.create()
                session_key = self.request.session.session_key
            
            cart, created = Order.objects.prefetch_related(
                'items__product__category',
                'items__product__images'
            ).get_or_create(
                session_key=session_key,
                status='CART',
                is_guest=True
            )
        return cart


# the order item manage view handles add to cart logic, and update quantity logic and locking price
class OrderItemManageView(generics.ListCreateAPIView):
    """API endpoint for managing order items in the cart (supports guests)."""
    serializer_class = OrderItemSerializer
    permission_classes = [AllowAny]  # Allow guests

    def get_queryset(self):
        # Optimized: get cart with prefetched items
        cart = self._get_or_create_cart()
        return OrderItem.objects.select_related(
            'product__category'
        ).prefetch_related(
            'product__images'
        ).filter(order=cart)
    
    def _get_or_create_cart(self):
        """Helper to get cart for authenticated or guest user (optimized)"""
        if self.request.user.is_authenticated:
            # Uses order_user_status_idx
            cart, _ = Order.objects.get_or_create(
                user=self.request.user,
                status='CART'
            )
        else:
            # Uses order_guest_cart_idx
            session_key = self.request.session.session_key
            if not session_key:
                self.request.session.create()
                session_key = self.request.session.session_key
            
            cart, _ = Order.objects.get_or_create(
                session_key=session_key,
                status='CART',
                is_guest=True
            )
        return cart

    def perform_create(self, serializer):
        quantity = serializer.validated_data.get('quantity', 1)
        product = serializer.context['product']

        # Get cart for authenticated or guest user
        cart = self._get_or_create_cart()

        # Check if product already in cart
        try:
            order_item = OrderItem.objects.get(order=cart, product=product)
            order_item.quantity += quantity
            order_item.save()
            serializer.instance = order_item
        except OrderItem.DoesNotExist:
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
        
        # Save contact information
        cart.first_name = serializer.validated_data.get('first_name', '')
        cart.last_name = serializer.validated_data.get('last_name', '')
        cart.phone_number = serializer.validated_data.get('phone_number', '')
        # Use provided email or fall back to user's email
        cart.email = serializer.validated_data.get('email', '') or request.user.email
        
        # Save address information
        cart.shipping_address = serializer.validated_data.get('shipping_address', '')
        cart.shipping_address_line_2 = serializer.validated_data.get('shipping_address_line_2', '')
        cart.shipping_city = serializer.validated_data.get('shipping_city', '')
        cart.shipping_state = serializer.validated_data.get('shipping_state', '')
        cart.shipping_postal_code = serializer.validated_data.get('shipping_postal_code', '')
        cart.shipping_country = serializer.validated_data.get('shipping_country', 'Morocco')
        
        # 4. Change status to PENDING
        cart.status = 'PENDING'
        cart.save()
        
        # 5. Queue order confirmation email (async)
        email_to_use = cart.email or request.user.email
        if email_to_use:
            send_order_confirmation_email.delay(str(cart.id))
        
        # 6. Return order for payment
        return Response({
            "message": "Order placed. Proceed to payment.",
            "order_id": str(cart.id),
            "total": float(cart.total_price)
        })

# Payment View

class MockPaymentView(generics.GenericAPIView):
    """For testing I will use : Mock payment- marks order as paid"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, order_id):
        try:
            order = Order.objects.get(
                id=order_id, 
                user=request.user, 
                status='PENDING'
            )
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found or not in pending status"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # "Process" payment (mock)
        order.status = 'PAID'
        order.payment_method = 'mock'
        order.payment_intent_id = f'mock_{order.id}'
        order.paid_at = timezone.now()
        order.save()
        
        return Response({
            "message": "Payment successful",
            "order_id": str(order.id),
            "status": order.status,
            "paid_at": order.paid_at
        })


# Order History Views

class OrderListView(generics.ListAPIView):
    """List all orders for the authenticated user (excluding CART status) - Optimized"""
    permission_classes = [IsAuthenticated]
    serializer_class = OrderDetailSerializer
    
    def get_queryset(self):
        # Optimized: uses order_user_status_idx and prefetch related data
        return Order.objects.select_related(
            'user'
        ).prefetch_related(
            'items__product__category',
            'items__product__images'
        ).filter(
            user=self.request.user
        ).exclude(
            status='CART'
        ).order_by('-created_at')  # Uses order_user_status_idx


class OrderDetailView(generics.RetrieveAPIView):
    """Get details of a specific order - Optimized"""
    permission_classes = [IsAuthenticated]
    serializer_class = OrderDetailSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        # Optimized: prefetch all related data
        return Order.objects.select_related(
            'user'
        ).prefetch_related(
            'items__product__category',
            'items__product__images'
        ).filter(
            user=self.request.user
        ).exclude(status='CART')


# Guest Checkout Views

class GuestCheckoutView(generics.GenericAPIView):
    """Guest checkout - creates order without user account"""
    permission_classes = [AllowAny]
    serializer_class = GuestCheckoutSerializer
    
    def post(self, request):
        # Get guest cart from session
        session_key = request.session.session_key
        if not session_key:
            return Response(
                {"error": "No cart found"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart = Order.objects.get(
                session_key=session_key,
                status='CART',
                is_guest=True
            )
        except Order.DoesNotExist:
            return Response(
                {"error": "No active cart found"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate cart has items
        if not cart.items.exists():
            return Response(
                {"error": "Cart is empty"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save shipping info and email
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save all fields from validated data
        for field, value in serializer.validated_data.items():
            setattr(cart, field, value)
        
        # Ensure guest_email is set from email field for guest orders
        email_value = serializer.validated_data.get('email', '')
        cart.guest_email = email_value
        # Also set the main email field for consistency
        cart.email = email_value
        cart.status = 'PENDING'
        cart.save()
        
        # Queue order confirmation email if email provided (async)
        email_to_use = cart.email or cart.guest_email
        if email_to_use:
            send_order_confirmation_email.delay(str(cart.id))
        
        return Response({
            "message": "Order placed successfully.",
            "order_id": str(cart.id),
            "total": float(cart.total_price),
            "email": cart.guest_email if cart.guest_email else None
        })


class GuestOrderLookupView(generics.GenericAPIView):
    """Allow guests to view their order by order ID (email optional for verification)"""
    permission_classes = [AllowAny]
    serializer_class = GuestOrderLookupSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order_id = serializer.validated_data['order_id']
        email = serializer.validated_data.get('email')
        
        try:
            # Build query filters
            filters = {
                'id': order_id,
                'is_guest': True
            }
            
            # Add email filter only if provided
            if email:
                filters['guest_email'] = email
            
            order = Order.objects.get(**filters)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Return order details
        order_serializer = OrderDetailSerializer(order, context={'request': request})
        return Response(order_serializer.data)


class LinkGuestOrdersView(generics.GenericAPIView):
    """Link guest orders to newly created account"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        # Find guest orders with same email
        guest_orders = Order.objects.filter(
            is_guest=True,
            guest_email=user.email,
            user__isnull=True
        )
        
        # Link orders to user
        count = guest_orders.update(
            user=user,
            is_guest=False
        )
        
        return Response({
            "message": f"Linked {count} previous orders to your account",
            "orders_linked": count
        })