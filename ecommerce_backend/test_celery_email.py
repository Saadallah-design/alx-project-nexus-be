#!/usr/bin/env python
"""
Test script for Celery email task.
This simulates sending an order confirmation email.
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_backend.settings')
django.setup()

from orders.tasks import send_order_confirmation_email
from orders.models import Order

def test_email_task():
    """Test the order confirmation email task with a real order."""
    
    # Get the most recent order
    try:
        order = Order.objects.latest('created_at')
        print(f"Found order: {order.id}")
        print(f"Order total: ${order.total_price}")
        print(f"Order status: {order.status}")
        
        # Queue the email task
        result = send_order_confirmation_email.delay(str(order.id))
        
        print(f"\n✅ Task queued successfully!")
        print(f"Task ID: {result.id}")
        print(f"\nCheck the Celery worker terminal to see the email output.")
        print(f"(In development mode, emails are printed to console)")
        
    except Order.DoesNotExist:
        print("❌ No orders found in database.")
        print("Create an order first through the API or Django admin.")

if __name__ == '__main__':
    test_email_task()
