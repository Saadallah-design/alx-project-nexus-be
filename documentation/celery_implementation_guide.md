# Celery Implementation Guide - Django E-commerce Backend

## 📋 Table of Contents
1. [What is Celery?](#what-is-celery)
2. [When to Use Celery](#when-to-use-celery)
3. [Architecture Overview](#architecture-overview)
4. [Installation & Setup](#installation--setup)
5. [Basic Configuration](#basic-configuration)
6. [Creating Tasks](#creating-tasks)
7. [Use Cases for This Project](#use-cases-for-this-project)
8. [Running Celery](#running-celery)
9. [Monitoring & Management](#monitoring--management)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

---

## What is Celery?

### 🎯 Simple Explanation
Celery is like having a team of workers that handle time-consuming tasks in the background, so your web server can respond to users immediately without waiting.

**Without Celery:**
```
User places order → Server sends email → User waits 3 seconds → Response ❌
```

**With Celery:**
```
User places order → Server queues email task → Instant response ✅
                  → Celery worker sends email in background
```

### Core Components

1. **Task** - A function you want to run asynchronously
2. **Broker** - Message queue (Redis or RabbitMQ) that stores tasks
3. **Worker** - Process that executes tasks from the queue
4. **Beat** - Scheduler for periodic tasks (cron-like)
5. **Result Backend** - Stores task results (optional)

---

## When to Use Celery

### ✅ Perfect Use Cases

1. **Email Sending**
   ```python
   # Bad: Blocks user for 2-3 seconds
   send_order_confirmation_email(order)
   
   # Good: Instant response, email sent in background
   send_order_confirmation_email.delay(order.id)
   ```

2. **Image/File Processing**
   - Resize product images
   - Generate thumbnails
   - Process CSV uploads

3. **External API Calls**
   - Payment gateway processing
   - Shipping rate calculations
   - SMS notifications

4. **Report Generation**
   - Export large datasets
   - Generate invoices
   - Analytics reports

5. **Periodic Tasks**
   - Send daily order summaries
   - Clean up expired carts
   - Update inventory from supplier API

6. **Heavy Computations**
   - Complex calculations
   - Data aggregations
   - Machine learning inference

### ❌ Don't Use Celery For

1. **Simple, fast operations** (< 100ms)
2. **Operations that need immediate results** for the response
3. **Database queries** that could be optimized instead

---

## Architecture Overview

```
┌─────────────┐
│   Django    │  1. User makes request
│   Server    │  2. Queues task to broker
└──────┬──────┘  3. Returns response immediately
       │
       ↓
┌─────────────┐
│    Redis    │  Message Broker
│   (Broker)  │  Stores task queue
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   Celery    │  Worker Process
│   Worker    │  Executes tasks
└─────────────┘
```

---

## Installation & Setup

### Step 1: Install Required Packages

```bash
# Activate virtual environment
source venv/bin/activate

# Install Celery with Redis support
pip install celery[redis]
pip install redis

# Update requirements.txt
pip freeze > requirements.txt
```

### Step 2: Install and Start Redis (Message Broker)

**macOS (using Homebrew):**
```bash
# Install Redis
brew install redis

# Start Redis service
brew services start redis

# Or run in foreground
redis-server
```

**Test Redis:**
```bash
redis-cli ping
# Should respond: PONG
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

---

## Basic Configuration

### Step 1: Create Celery Configuration

```python
# ecommerce_backend/ecommerce_backend/celery.py

import os
from celery import Celery

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_backend.settings')

# Create Celery app
app = Celery('ecommerce_backend')

# Load configuration from Django settings using CELERY_ namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to test Celery setup"""
    print(f'Request: {self.request!r}')
```

### Step 2: Initialize Celery in Django

```python
# ecommerce_backend/ecommerce_backend/__init__.py

# This will make sure the Celery app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

__all__ = ('celery_app',)
```

### Step 3: Add Celery Settings

```python
# ecommerce_backend/ecommerce_backend/settings.py

# Add at the end of the file

# ===========================
# CELERY CONFIGURATION
# ===========================

# Celery Broker URL (Redis)
CELERY_BROKER_URL = 'redis://localhost:6379/0'

# Celery Result Backend (optional - stores task results)
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Accept JSON only (security best practice)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Timezone
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True

# Task result expiration time (1 day)
CELERY_RESULT_EXPIRES = 86400

# Task execution options
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes hard limit
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes soft limit

# Worker configuration
CELERY_WORKER_PREFETCH_MULTIPLIER = 4
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000  # Restart worker after 1000 tasks

# Beat scheduler (for periodic tasks)
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Optional: Task routing (advanced)
# CELERY_TASK_ROUTES = {
#     'orders.tasks.send_order_email': {'queue': 'emails'},
#     'orders.tasks.process_payment': {'queue': 'payments'},
# }
```

---

## Creating Tasks

### Basic Task Structure

```python
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
        
        send_mail(
            subject=f'Order Confirmation #{order.id}',
            message=f'Thank you for your order!\n\nOrder ID: {order.id}\nTotal: ${order.total_price}',
            from_email='noreply@ecommerce.com',
            recipient_list=[order.email or order.user.email],
            fail_silently=False,
        )
        
        return f'Email sent for order {order_id}'
    except Order.DoesNotExist:
        return f'Order {order_id} not found'
    except Exception as e:
        # Task will retry automatically if it raises an exception
        raise
```

### Using Tasks in Views

```python
# orders/views.py

from .tasks import send_order_confirmation_email

class CheckoutView(generics.GenericAPIView):
    def post(self, request):
        # ... checkout logic ...
        
        # Queue email task (non-blocking)
        send_order_confirmation_email.delay(order.id)
        
        # Return response immediately
        return Response({
            "message": "Order placed successfully",
            "order_id": str(order.id)
        })
```

---

## Use Cases for This Project

### 1. Order Confirmation Emails

```python
# orders/tasks.py

from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Order

@shared_task(bind=True, max_retries=3)
def send_order_confirmation_email(self, order_id):
    """Send HTML order confirmation email with retry logic."""
    try:
        order = Order.objects.select_related('user').prefetch_related(
            'items__product'
        ).get(id=order_id)
        
        # Don't send if no email
        email = order.email or (order.user.email if order.user else None)
        if not email:
            return 'No email address provided'
        
        # Render HTML email template
        html_content = render_to_string('emails/order_confirmation.html', {
            'order': order,
            'items': order.items.all(),
        })
        
        # Create email
        email_msg = EmailMultiAlternatives(
            subject=f'Order Confirmation - Order #{order.id}',
            body=f'Thank you for your order! Order ID: {order.id}',
            from_email='orders@ecommerce.com',
            to=[email]
        )
        email_msg.attach_alternative(html_content, "text/html")
        email_msg.send()
        
        return f'Confirmation email sent to {email}'
        
    except Order.DoesNotExist:
        return f'Order {order_id} not found'
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

### 2. Guest Order Notification

```python
@shared_task
def send_guest_order_tracking_info(order_id):
    """Send order tracking info to guest users."""
    order = Order.objects.get(id=order_id)
    
    if order.is_guest and order.guest_email:
        send_mail(
            subject='Track Your Order',
            message=f'Track your order using ID: {order.id}\n'
                    f'Visit: https://ecommerce.com/track?id={order.id}',
            from_email='noreply@ecommerce.com',
            recipient_list=[order.guest_email],
        )
```

### 3. Product Image Processing

```python
# catalog/tasks.py

from celery import shared_task
from PIL import Image
from .models import ProductImage
import os

@shared_task
def generate_product_thumbnails(product_image_id):
    """Generate thumbnail versions of product images."""
    try:
        product_image = ProductImage.objects.get(id=product_image_id)
        img = Image.open(product_image.image.path)
        
        # Generate thumbnail (300x300)
        thumbnail_size = (300, 300)
        img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
        
        # Save thumbnail
        thumb_path = product_image.image.path.replace('.jpg', '_thumb.jpg')
        img.save(thumb_path, 'JPEG', quality=85)
        
        return f'Thumbnail generated for {product_image_id}'
    except Exception as e:
        return f'Error: {str(e)}'
```

### 4. Clean Up Expired Carts (Periodic Task)

```python
# orders/tasks.py

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Order

@shared_task
def cleanup_expired_carts():
    """Delete carts older than 30 days."""
    cutoff_date = timezone.now() - timedelta(days=30)
    
    expired_carts = Order.objects.filter(
        status='CART',
        created_at__lt=cutoff_date
    )
    
    count = expired_carts.count()
    expired_carts.delete()
    
    return f'Deleted {count} expired carts'
```

### 5. Low Stock Alerts

```python
# catalog/tasks.py

from celery import shared_task
from django.core.mail import mail_admins
from .models import Product

@shared_task
def check_low_stock_products():
    """Send alert for products with low stock."""
    low_stock_products = Product.objects.filter(
        stock_quantity__lte=5,
        is_available=True
    )
    
    if low_stock_products.exists():
        product_list = '\n'.join([
            f'{p.name}: {p.stock_quantity} left'
            for p in low_stock_products
        ])
        
        mail_admins(
            subject='Low Stock Alert',
            message=f'Low stock products:\n\n{product_list}'
        )
        
        return f'Alert sent for {low_stock_products.count()} products'
    
    return 'No low stock products'
```

### 6. Payment Processing with Retry

```python
# orders/tasks.py

from celery import shared_task
import stripe

@shared_task(bind=True, max_retries=5)
def process_stripe_payment(self, order_id, payment_intent_id):
    """Process Stripe payment with retry logic."""
    try:
        order = Order.objects.get(id=order_id)
        
        # Confirm payment with Stripe
        payment_intent = stripe.PaymentIntent.confirm(payment_intent_id)
        
        if payment_intent.status == 'succeeded':
            order.status = 'PAID'
            order.paid_at = timezone.now()
            order.payment_intent_id = payment_intent_id
            order.save()
            
            # Queue confirmation email
            send_order_confirmation_email.delay(order_id)
            
            return f'Payment processed for order {order_id}'
        else:
            raise Exception(f'Payment failed: {payment_intent.status}')
            
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=10 * (2 ** self.request.retries))
```

---

## Running Celery

### Development (Single Window)

```bash
# Terminal 1: Start Django
cd ecommerce_backend
python manage.py runserver

# Terminal 2: Start Redis (if not running as service)
redis-server

# Terminal 3: Start Celery Worker
cd /Users/salah-eddinesaadalla/repos/alx-projects/alx-project-nexus-be
source venv/bin/activate
cd ecommerce_backend
celery -A ecommerce_backend worker --loglevel=info
```

### Development (Easier - All in One)

```bash
# Start worker with auto-reload (for development)
celery -A ecommerce_backend worker --loglevel=info --pool=solo
```

### Periodic Tasks (Beat Scheduler)

First, install django-celery-beat:
```bash
pip install django-celery-beat
pip freeze > requirements.txt
```

Add to settings:
```python
INSTALLED_APPS = [
    # ...
    'django_celery_beat',
]
```

Run migrations:
```bash
python manage.py migrate django_celery_beat
```

Start beat scheduler:
```bash
# Terminal 4: Start Celery Beat
celery -A ecommerce_backend beat --loglevel=info
```

### Production Setup

```bash
# Worker with multiple processes
celery -A ecommerce_backend worker --loglevel=info --concurrency=4

# Worker as daemon (background)
celery -A ecommerce_backend worker --loglevel=info --detach

# With supervisor (recommended for production)
# See production section below
```

---

## Monitoring & Management

### Flower - Web-based Monitoring

```bash
# Install Flower
pip install flower

# Start Flower
celery -A ecommerce_backend flower

# Access at: http://localhost:5555
```

**Flower shows:**
- Active/completed/failed tasks
- Worker status
- Task execution time
- Success/failure rates

### Django Admin Integration

Register tasks in admin:
```python
# orders/admin.py

from django_celery_beat.models import PeriodicTask, IntervalSchedule

admin.site.register(PeriodicTask)
admin.site.register(IntervalSchedule)
```

Now you can create periodic tasks from Django admin!

### Useful Celery Commands

```bash
# Inspect active tasks
celery -A ecommerce_backend inspect active

# Inspect registered tasks
celery -A ecommerce_backend inspect registered

# Revoke a task
celery -A ecommerce_backend control revoke <task-id>

# Purge all tasks
celery -A ecommerce_backend purge

# Worker statistics
celery -A ecommerce_backend inspect stats
```

---

## Best Practices

### 1. **Always Pass IDs, Not Objects**

```python
# ❌ BAD: Can't serialize Order object
send_email.delay(order)

# ✅ GOOD: Pass the ID
send_email.delay(order.id)
```

### 2. **Handle Errors Gracefully**

```python
@shared_task(bind=True, max_retries=3)
def my_task(self, data):
    try:
        # Task logic
        pass
    except Exception as exc:
        # Log error
        logger.error(f'Task failed: {exc}')
        # Retry with backoff
        raise self.retry(exc=exc, countdown=60)
```

### 3. **Set Task Time Limits**

```python
@shared_task(time_limit=300, soft_time_limit=270)
def long_running_task():
    # Will be killed after 5 minutes
    pass
```

### 4. **Use Task Names for Routing**

```python
@shared_task(name='orders.send_email', queue='emails')
def send_email(order_id):
    pass
```

### 5. **Idempotent Tasks**

Make sure tasks can be safely retried:
```python
@shared_task
def update_order_status(order_id, status):
    # Safe to run multiple times
    Order.objects.filter(id=order_id).update(status=status)
```

### 6. **Monitor Task Performance**

```python
@shared_task
def monitored_task():
    from time import time
    start = time()
    
    # Task logic
    
    duration = time() - start
    logger.info(f'Task completed in {duration}s')
```

---

## Troubleshooting

### Issue: Tasks Not Executing

**Check:**
```bash
# Is Redis running?
redis-cli ping

# Is Celery worker running?
celery -A ecommerce_backend inspect active

# Check logs
celery -A ecommerce_backend worker --loglevel=debug
```

### Issue: ModuleNotFoundError

**Solution:**
```bash
# Make sure you're in the right directory
cd ecommerce_backend

# Check DJANGO_SETTINGS_MODULE
export DJANGO_SETTINGS_MODULE=ecommerce_backend.settings
```

### Issue: Tasks Hang Forever

**Solution:**
Set task time limits in settings.py:
```python
CELERY_TASK_TIME_LIMIT = 300  # 5 minutes
```

### Issue: Memory Leaks

**Solution:**
Restart workers periodically:
```python
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
```

---

## Production Deployment

### Using Supervisor (Recommended)

```bash
# Install supervisor
sudo apt install supervisor

# Create config file: /etc/supervisor/conf.d/celery.conf
```

```ini
[program:celery_worker]
command=/path/to/venv/bin/celery -A ecommerce_backend worker --loglevel=info
directory=/path/to/ecommerce_backend
user=www-data
autostart=true
autorestart=true
stdout_logfile=/var/log/celery/worker.log
stderr_logfile=/var/log/celery/worker_error.log

[program:celery_beat]
command=/path/to/venv/bin/celery -A ecommerce_backend beat --loglevel=info
directory=/path/to/ecommerce_backend
user=www-data
autostart=true
autorestart=true
stdout_logfile=/var/log/celery/beat.log
stderr_logfile=/var/log/celery/beat_error.log
```

```bash
# Start services
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start celery_worker
sudo supervisorctl start celery_beat
```

---

## Quick Start Checklist

- [ ] Install Redis and start service
- [ ] Install celery and redis packages
- [ ] Create celery.py in project root
- [ ] Update __init__.py to import celery app
- [ ] Add Celery settings to settings.py
- [ ] Create tasks.py in your app
- [ ] Start Celery worker
- [ ] Test task execution
- [ ] Optional: Install Flower for monitoring
- [ ] Optional: Install django-celery-beat for periodic tasks

---

## Summary

### Key Concepts
1. **Async Tasks** - Background processing
2. **Message Broker** - Redis queues tasks
3. **Workers** - Execute tasks
4. **Beat** - Schedule periodic tasks
5. **Monitoring** - Flower/Django admin

### Common Commands
```bash
# Start worker
celery -A ecommerce_backend worker -l info

# Start beat
celery -A ecommerce_backend beat -l info

# Start flower
celery -A ecommerce_backend flower

# Test task
python manage.py shell
>>> from orders.tasks import send_order_confirmation_email
>>> send_order_confirmation_email.delay('order-id')
```

### Next Steps
1. Implement email tasks
2. Add periodic cleanup tasks
3. Monitor with Flower
4. Deploy to production with supervisor

**Celery makes your app faster, more scalable, and provides better user experience!** 🚀
