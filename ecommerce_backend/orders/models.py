from django.db import models
from django.conf import settings
import uuid
from catalog.models import Product 
# Link to the product being purchased (from the catalog app)


# will be creating two models for the order process
# order and orderItem



# ---- Order Model ----
class Order(models.Model):
    # setting a unique UUID for the order
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    # using customUserModel defined in settings.py (users.CustomUser) |
    #  (retrieved via settings.AUTH_USER_MODEL)
    # Nullable for guest orders
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='orders',
        null=True,
        blank=True
    )
    
    # Guest order fields
    is_guest = models.BooleanField(default=False)
    guest_email = models.EmailField(blank=True)
    session_key = models.CharField(max_length=40, blank=True, help_text="Session key for guest cart tracking")

    # setting up the order model for the checkout flow
    # Contact Information
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    # Shipping Fields
    shipping_address = models.CharField(max_length=255, blank=True)
    shipping_address_line_2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100, blank=True)
    shipping_state = models.CharField(max_length=100, blank=True)
    shipping_postal_code = models.CharField(max_length=20, blank=True)
    shipping_country = models.CharField(max_length=100, default='Morocco')

# Status of the order
    STATUS_CHOICES = (
        ('CART', 'Shopping Cart'),
        ('PENDING', 'Pending Payment'),
        ('PAID', 'Paid/Processing'),
        ('SHIPPED', 'Shipped'),
        ('CANCELLED', 'Cancelled'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='CART')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Property to calculate the total price of all items in the order | Dynamic
    @property
    def total_price(self):
        # items.all accesses the related order items
        # item.extended_price is the price of the item * quantity extended from the OrderItem model
        return sum(item.extended_price for item in self.items.all())

    def __str__(self):
        return f"Order {self.id} - Status: {self.status}"

    # payment tracking part
    payment_method = models.CharField(max_length=50, blank=True)  # to try: 'mock', 'stripe', 'paypal'
    payment_intent_id = models.CharField(max_length=255, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)


# ---- OrderItem Model ----
class OrderItem(models.Model):
    # Linking it back to the parent order/cart
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    # using string import of catalog.Product to avoid import erros
    product = models.ForeignKey('catalog.Product', on_delete=models.PROTECT) # Prevents deleting a product that's been ordered 
    quantity = models.PositiveIntegerField(default=1)
    
    # Price saved at the time the item was added to the order/cart.
    # (Price locking): This ensures the price is locked and doesn't change later if the catalog price updates.
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    
    @property
    def extended_price(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.order.id}"

    class Meta:
        unique_together = ('order', 'product') # A cart/order should not have the same product listed twice.


