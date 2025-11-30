# Email Configuration Guide - Django E-commerce Backend

## 📧 Current Status

**Development Mode (Default):**
- Emails are printed to console (Celery worker terminal)
- No real emails are sent
- Good for testing without SMTP setup

**Production Mode:**
- Real emails sent via SMTP
- Requires email provider configuration
- Users receive actual emails

---

## 🚀 Quick Setup Guide

### Option 1: Keep Console Backend (Development)
**Current setup - no changes needed!**

```bash
# Emails print to Celery worker terminal
# Easy for testing, no configuration required
```

### Option 2: Enable Real Email Sending

#### Step 1: Choose Email Provider

**Popular Options:**
1. **Gmail** (easiest for testing)
2. **SendGrid** (recommended for production)
3. **AWS SES** (cost-effective for scale)
4. **Mailgun** (developer-friendly)
5. **Custom SMTP** (your own mail server)

---

## 📮 Gmail Setup (Easiest for Testing)

### Step 1: Enable App Password

1. Go to Google Account settings
2. Security → 2-Step Verification (enable if not already)
3. App passwords → Generate new password
4. Select "Mail" and "Other" (Django App)
5. Copy the 16-character password

### Step 2: Update `.env` File

```bash
# Open ecommerce_backend/.env and add:

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx  # 16-char app password
DEFAULT_FROM_EMAIL=noreply@ecommerce.com
```

### Step 3: Enable SMTP in Settings

**Option A: Test in Development**
```python
# ecommerce_backend/settings.py
# Uncomment the testing section at the bottom of EMAIL CONFIGURATION
```

**Option B: Use in Production**
```bash
# Set DEBUG=False in .env
DEBUG=False
```

### Step 4: Restart Services

```bash
# 1. Restart Django
python manage.py runserver

# 2. Restart Celery worker
celery -A ecommerce_backend worker --loglevel=info --pool=solo
```

### Step 5: Test Real Email

```bash
cd ecommerce_backend
python quick_test_email.py
# Check your actual email inbox!
```

---

## 🎯 SendGrid Setup (Production Recommended)

### Why SendGrid?
- ✅ Free tier: 100 emails/day
- ✅ Better deliverability than Gmail
- ✅ Email analytics dashboard
- ✅ No 2FA or app password hassle
- ✅ Designed for transactional emails

### Step 1: Create Account
1. Sign up at https://sendgrid.com
2. Verify your email
3. Complete sender authentication

### Step 2: Create API Key
1. Settings → API Keys → Create API Key
2. Name it "Django Ecommerce"
3. Full Access (or Mail Send permission)
4. Copy the API key (shows once!)

### Step 3: Update `.env`

```bash
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey  # Literally the word "apikey"
EMAIL_HOST_PASSWORD=SG.xxxxxxxxxxxxxxxxxxx  # Your API key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com  # Your verified domain
```

### Step 4: Verify Sender Domain (Important!)

SendGrid requires sender verification:

1. **Single Sender Verification** (Quick):
   - Settings → Sender Authentication
   - Verify single sender email
   - Good for testing

2. **Domain Authentication** (Production):
   - Add DNS records to your domain
   - Better deliverability
   - Required for higher volume

---

## 🌩️ AWS SES Setup (Cost-Effective Scale)

### Pricing
- $0.10 per 1,000 emails
- First 62,000 emails/month free (if sent from EC2)

### Setup Steps

```bash
# Install boto3
pip install boto3
pip freeze > requirements.txt
```

Update `.env`:
```bash
EMAIL_BACKEND=django_ses.SESBackend
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_SES_REGION_NAME=us-east-1
AWS_SES_REGION_ENDPOINT=email.us-east-1.amazonaws.com
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

Install django-ses:
```bash
pip install django-ses
```

Update settings.py:
```python
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_SES_REGION_NAME = env('AWS_SES_REGION_NAME', default='us-east-1')
AWS_SES_REGION_ENDPOINT = env('AWS_SES_REGION_ENDPOINT')
```

---

## 📊 Comparison Table

| Provider | Free Tier | Setup | Best For | Deliverability |
|----------|-----------|-------|----------|----------------|
| **Gmail** | 500/day | Easy | Testing | Good |
| **SendGrid** | 100/day | Medium | Production | Excellent |
| **AWS SES** | 62k/month* | Medium | Scale | Excellent |
| **Mailgun** | 5k/month | Medium | Production | Excellent |
| **Console** | Unlimited | None | Development | N/A |

*From EC2 instance

---

## 🧪 Testing Email Configuration

### Test Script
```bash
cd ecommerce_backend
python manage.py shell
```

```python
from django.core.mail import send_mail

# Test email
send_mail(
    subject='Test Email from Django',
    message='If you receive this, email is working!',
    from_email='noreply@ecommerce.com',
    recipient_list=['your-email@example.com'],
    fail_silently=False,
)
```

### Expected Results

**Console Backend:**
```
Content-Type: text/plain; charset="utf-8"
Subject: Test Email from Django
From: noreply@ecommerce.com
To: your-email@example.com

If you receive this, email is working!
```

**SMTP Backend:**
- Check your email inbox
- Email should arrive within seconds
- Check spam folder if not in inbox

---

## 🔧 Troubleshooting

### Issue: "SMTPAuthenticationError"

**Gmail:**
```bash
# Solution 1: Enable "Less secure app access"
# (Not recommended - use App Password instead)

# Solution 2: Create App Password (RECOMMENDED)
1. Enable 2-Step Verification
2. Generate App Password
3. Use 16-char password in .env
```

**SendGrid:**
```bash
# Check:
1. API key is correct
2. EMAIL_HOST_USER=apikey (literal word)
3. Sender email is verified
```

### Issue: Emails Go to Spam

**Solutions:**
1. **Verify domain** (SPF, DKIM, DMARC records)
2. **Use professional from address** (not @gmail.com in production)
3. **Warm up IP** (send gradually increasing volume)
4. **Add unsubscribe link** (improves trust)

### Issue: "Connection refused"

```bash
# Check:
1. EMAIL_PORT is correct (587 for TLS, 465 for SSL)
2. EMAIL_USE_TLS or EMAIL_USE_SSL is set
3. Firewall allows outbound SMTP connections
4. SMTP credentials are correct
```

### Issue: Emails Slow to Send

```bash
# This is why we use Celery!
# Emails are async - user doesn't wait

# But if Celery is slow:
1. Check Redis is running: redis-cli ping
2. Check Celery worker is running: jobs
3. Check Celery logs for errors
```

---

## 🎨 Production Email Template (HTML)

### Create HTML Email Template

```python
# orders/tasks.py

from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Order

@shared_task
def send_order_confirmation_email(order_id):
    """Send beautiful HTML order confirmation email."""
    try:
        order = Order.objects.select_related('user').prefetch_related(
            'items__product'
        ).get(id=order_id)
        
        # Get email
        email = order.email or (order.user.email if order.user else None)
        if not email:
            return f'No email for order {order_id}'
        
        # Render HTML template
        html_content = render_to_string('emails/order_confirmation.html', {
            'order': order,
            'items': order.items.all(),
            'total': order.total_price,
        })
        
        # Plain text fallback
        text_content = f'''
        Thank you for your order!
        
        Order ID: {order.id}
        Total: ${order.total_price}
        
        Order Details:
        {chr(10).join([f"- {item.product.name} x{item.quantity}: ${item.extended_price}" for item in order.items.all()])}
        
        We'll send you another email when your order ships!
        '''
        
        # Create email
        email_msg = EmailMultiAlternatives(
            subject=f'Order Confirmation - #{order.id}',
            body=text_content,
            from_email='noreply@ecommerce.com',
            to=[email]
        )
        email_msg.attach_alternative(html_content, "text/html")
        email_msg.send()
        
        return f'Email sent to {email}'
        
    except Order.DoesNotExist:
        return f'Order {order_id} not found'
    except Exception as e:
        raise  # Celery will retry
```

### Create Template File

```html
<!-- ecommerce_backend/templates/emails/order_confirmation.html -->

<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #4CAF50; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9f9f9; }
        .order-item { border-bottom: 1px solid #ddd; padding: 10px 0; }
        .total { font-size: 1.5em; font-weight: bold; color: #4CAF50; }
        .footer { text-align: center; padding: 20px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Thank You for Your Order! 🎉</h1>
        </div>
        
        <div class="content">
            <p>Hi {{ order.first_name }},</p>
            
            <p>Your order has been confirmed and will be processed soon.</p>
            
            <h3>Order Details</h3>
            <p><strong>Order ID:</strong> {{ order.id }}</p>
            <p><strong>Date:</strong> {{ order.created_at|date:"F d, Y" }}</p>
            
            <h3>Items</h3>
            {% for item in items %}
            <div class="order-item">
                <strong>{{ item.product.name }}</strong><br>
                Quantity: {{ item.quantity }} × ${{ item.price }}<br>
                Subtotal: ${{ item.extended_price }}
            </div>
            {% endfor %}
            
            <p class="total">Total: ${{ total }}</p>
            
            <h3>Shipping Address</h3>
            <p>
                {{ order.shipping_address }}<br>
                {{ order.shipping_city }}, {{ order.shipping_state }} {{ order.shipping_postal_code }}<br>
                {{ order.shipping_country }}
            </p>
        </div>
        
        <div class="footer">
            <p>Need help? Contact us at support@ecommerce.com</p>
            <p>&copy; 2025 E-commerce. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
```

---

## 📈 Production Checklist

Before deploying to production with real emails:

- [ ] Choose email provider (SendGrid/AWS SES recommended)
- [ ] Set up sender authentication (SPF/DKIM/DMARC)
- [ ] Verify sending domain
- [ ] Test email deliverability
- [ ] Create HTML email templates
- [ ] Add unsubscribe links (legal requirement)
- [ ] Set up email monitoring/logging
- [ ] Configure email rate limits
- [ ] Test spam score (mail-tester.com)
- [ ] Set DEBUG=False in production
- [ ] Update DEFAULT_FROM_EMAIL to real domain

---

## 🎯 Quick Decision Guide

**"I just want to test locally"**
→ Keep console backend (no setup needed!)

**"I want to test real emails quickly"**
→ Use Gmail with App Password

**"I'm deploying to production soon"**
→ Set up SendGrid or AWS SES

**"I need to send 10,000+ emails/month"**
→ Use AWS SES (cheapest at scale)

---

## 📝 Summary

### Current Setup (Development)
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Emails print to Celery worker terminal
# ✅ No configuration needed
# ❌ Users don't receive real emails
```

### Production Setup
```bash
# 1. Add to .env:
EMAIL_HOST=smtp.sendgrid.net
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# 2. Set DEBUG=False

# 3. Restart services

# ✅ Users receive real emails
# ✅ Better deliverability
# ✅ Email analytics
```

---

## 🚀 Next Steps

1. **For Testing**: Keep current console backend
2. **For Production**: Follow SendGrid setup guide above
3. **Optional**: Create HTML email templates for better UX
4. **Monitor**: Set up email delivery monitoring in production

**Ready when you are!** The current setup works perfectly for development. Add SMTP when you're ready to send real emails! 📧
