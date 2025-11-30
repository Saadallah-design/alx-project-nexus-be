#!/usr/bin/env python
"""
Debug email sending to zize.access@gmail.com
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_backend.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
import traceback

print("="*60)
print("DEBUG: EMAIL TO ZIZE.ACCESS@GMAIL.COM")
print("="*60)

print("\n📋 Email Configuration:")
print(f"   Backend: {settings.EMAIL_BACKEND}")
print(f"   Host: {settings.EMAIL_HOST}")
print(f"   Port: {settings.EMAIL_PORT}")
print(f"   Use TLS: {settings.EMAIL_USE_TLS}")
print(f"   User: {settings.EMAIL_HOST_USER}")
print(f"   From: {settings.DEFAULT_FROM_EMAIL}")

print("\n📧 Sending test email directly...")

try:
    result = send_mail(
        subject='🎉 Order Confirmation - Test from Django Backend',
        message='''
Hello Zize!

This is a test order confirmation email from the Django e-commerce backend.

Order Details:
- Order ID: TEST-001
- Product: Jellaba Test × 2
- Total: $599.98
- Status: Confirmed

Thank you for testing the email system!

If you receive this email, the system is working correctly.

Best regards,
E-commerce Team
        ''',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['zize.access@gmail.com'],
        fail_silently=False,
    )
    
    print("\n" + "="*60)
    print("✅ EMAIL SENT SUCCESSFULLY!")
    print("="*60)
    print(f"\nResult: {result} email(s) sent")
    print("\n📬 Recipient: zize.access@gmail.com")
    print("\n⏱️  Email should arrive within 1-2 minutes")
    print("\n🔍 If not received, check:")
    print("   1. Inbox")
    print("   2. Spam/Junk folder")
    print("   3. Promotions tab (Gmail)")
    print("   4. All Mail folder")
    print("="*60)
    
except Exception as e:
    print("\n" + "="*60)
    print("❌ EMAIL SENDING FAILED")
    print("="*60)
    print(f"\nError: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    print("="*60)
