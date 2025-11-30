# orders/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from .models import Order

@shared_task
def send_order_confirmation_email(order_id):
    """
    Send order confirmation email asynchronously.
    
    Args:
        order_id: UUID of the order
    """
    try:
        order = Order.objects.get(id=order_id)
        
        # Get email address (handle both guest and authenticated users)
        email = None
        if order.email:
            email = order.email
        elif order.user and order.user.email:
            email = order.user.email
        
        if not email:
            return f'No email address for order {order_id} - skipping email'
        
        send_mail(
            subject=f'Order Confirmation #{order.id}',
            message=f'Thank you for your order!\n\nOrder ID: {order.id}\nTotal: ${order.total_price}',
            from_email='noreply@ecommerce.com',
            recipient_list=[email],
            fail_silently=False,
        )
        
        return f'Email sent to {email} for order {order_id}'
    except Order.DoesNotExist:
        return f'Order {order_id} not found'
    except Exception as e:
        # Task will retry automatically if it raises an exception
        raise