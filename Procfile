web: cd ecommerce_backend && python manage.py migrate && python manage.py import_products && gunicorn ecommerce_backend.wsgi --log-file -
worker: cd ecommerce_backend && celery -A ecommerce_backend worker --loglevel=info
