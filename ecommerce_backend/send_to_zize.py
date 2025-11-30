#!/usr/bin/env python
"""
Create a test order and send real email to zize.access@gmail.com
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_backend.settings')
django.setup()

from orders.models import Order, OrderItem
from catalog.models import Product
from orders.tasks import send_order_confirmation_email

def create_order_for_zize():
    """Create test order and send email to zize.access@gmail.com"""
    
    print("="*60)
    print("CREATING ORDER FOR ZIZE.ACCESS@GMAIL.COM")
    print("="*60)
    
    # Get a product
    products = Product.objects.filter(is_available=True)[:1]
    if not products:
        print("❌ No products available")
        return
    
    product = products[0]
    
    # Create order
    order = Order.objects.create(
        email='zize.access@gmail.com',
        is_guest=True,
        status='PENDING',
        first_name='Zize',
        last_name='Customer',
        phone_number='+1234567890',
        shipping_address='123 Main Street',
        shipping_city='New York',
        shipping_state='NY',
        shipping_postal_code='10001',
        shipping_country='USA'
    )
    
    # Add item
    OrderItem.objects.create(
        order=order,
        product=product,
        quantity=2,
        price=product.base_price
    )
    
    print(f"\n✅ Order Created Successfully!")
    print(f"   Order ID: {order.id}")
    print(f"   Email: {order.email}")
    print(f"   Status: {order.status}")
    print(f"   Product: {product.name}")
    print(f"   Quantity: 2")
    print(f"   Total: ${order.total_price}")
    
    # Queue email task
    print(f"\n📧 Sending confirmation email to {order.email}...")
    result = send_order_confirmation_email.delay(str(order.id))
    
    print(f"\n✅ Email task queued!")
    print(f"   Task ID: {result.id}")
    print(f"\n📬 REAL EMAIL WILL BE SENT TO: zize.access@gmail.com")
    print(f"\n⏱️  Email should arrive within seconds!")
    print(f"   (Check spam folder if not in inbox)")
    print("="*60)
    
    return order

if __name__ == '__main__':
    try:
        order = create_order_for_zize()
        print("\n✅ SUCCESS! Check zize.access@gmail.com inbox!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
