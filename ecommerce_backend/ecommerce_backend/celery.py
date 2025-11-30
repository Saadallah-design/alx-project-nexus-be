# ecommerce_backend/ecommerce_backend/celery.py

import os
from celery import Celery

# Setting default Django settings module
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
