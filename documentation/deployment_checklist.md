# Django E-commerce Backend - Deployment Checklist

> [!CAUTION]
> This checklist contains critical security and performance configurations. Skipping items can lead to security vulnerabilities, data breaches, or application failures in production.

---

## 🔒 Security Configuration

### 1. **Environment Variables**

> [!IMPORTANT]
> Never commit `.env` files or hardcode secrets in your codebase!

**Required Actions:**
- [ ] Generate a new `SECRET_KEY` for production (different from development)
  ```bash
  python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
  ```
- [ ] Set `DEBUG=False` in production `.env`
- [ ] Configure production database credentials
- [ ] Store environment variables securely (use platform secrets manager)

**Example Production `.env`:**
```bash
SECRET_KEY="your-production-secret-key-here"
DEBUG=False
DATABASE_URL="postgres://user:password@host:port/dbname"
ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"
```

---

### 2. **Django Settings** ([settings.py](file:///Users/salah-eddinesaadalla/repos/alx-projects/alx-project-nexus-be/ecommerce_backend/ecommerce_backend/settings.py))

**Critical Settings:**
- [ ] `DEBUG = False` (MUST be False in production)
- [ ] `ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']` (configure your domains)
- [ ] `SECRET_KEY` - Use environment variable, never hardcode
- [ ] Remove or secure Django admin URL (change from `/admin/` to something obscure)

**Add to settings.py:**
```python
# Security Settings for Production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

---

### 3. **CORS Configuration**

> [!WARNING]
> Misconfigured CORS can expose your API to unauthorized access!

- [ ] Install `django-cors-headers`: `pip install django-cors-headers`
- [ ] Add to `INSTALLED_APPS`: `'corsheaders'`
- [ ] Add to `MIDDLEWARE`: `'corsheaders.middleware.CorsMiddleware'` (before CommonMiddleware)
- [ ] Configure allowed origins:

```python
# Don't use CORS_ALLOW_ALL_ORIGINS = True in production!
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]

# For credentials (cookies, authentication)
CORS_ALLOW_CREDENTIALS = True
```

---

### 4. **Database Security**

- [ ] Use strong database passwords (minimum 16 characters, mixed case, numbers, symbols)
- [ ] Enable SSL/TLS for database connections
- [ ] Restrict database access by IP (whitelist only your application servers)
- [ ] Regular database backups configured
- [ ] Database user has minimum required permissions (not superuser)

**PostgreSQL SSL Connection:**
```python
DATABASES = {
    'default': {
        **env.db(),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}
```

---

## 📦 Static Files & Media

### 5. **Static Files Configuration**

- [ ] Configure `STATIC_ROOT` for collectstatic
- [ ] Configure `STATIC_URL` with CDN if using one
- [ ] Run `python manage.py collectstatic` before deployment
- [ ] Serve static files via CDN or web server (Nginx/Apache), not Django

**Add to settings.py:**
```python
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

# If using WhiteNoise for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

---

### 6. **Media Files Configuration**

- [ ] Configure `MEDIA_ROOT` and `MEDIA_URL`
- [ ] Use cloud storage (AWS S3, Google Cloud Storage) for production
- [ ] Set proper file upload size limits
- [ ] Validate file types on upload

**Example with django-storages (S3):**
```python
# Install: pip install django-storages boto3
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME')
```

---

## 🚀 Performance Optimization

### 7. **Database Optimization**

- [ ] Add database indexes to frequently queried fields
- [ ] Enable database connection pooling
- [ ] Configure `CONN_MAX_AGE` for persistent connections

```python
DATABASES = {
    'default': {
        **env.db(),
        'CONN_MAX_AGE': 600,  # 10 minutes
    }
}
```

---

### 8. **Caching**

- [ ] Configure Redis or Memcached for caching
- [ ] Cache database queries
- [ ] Cache API responses where appropriate

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

---

### 9. **Gunicorn/uWSGI Configuration**

- [ ] Use production WSGI server (Gunicorn or uWSGI)
- [ ] Configure worker processes (2-4 × CPU cores)
- [ ] Set appropriate timeout values
- [ ] Configure worker class (sync, async, gevent)

**Example Gunicorn command:**
```bash
gunicorn ecommerce_backend.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
```

---

## 🔐 Authentication & JWT

### 10. **JWT Configuration**

- [ ] Configure appropriate token lifetimes
- [ ] Use refresh tokens
- [ ] Implement token blacklisting for logout
- [ ] Rotate signing keys periodically

**Add to settings.py:**
```python
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

---

## 📊 Monitoring & Logging

### 11. **Logging Configuration**

- [ ] Configure production logging
- [ ] Set up error tracking (Sentry, Rollbar)
- [ ] Log to external service (CloudWatch, Papertrail)
- [ ] Monitor application performance

**Example logging config:**
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

---

### 12. **Error Tracking**

- [ ] Install Sentry: `pip install sentry-sdk`
- [ ] Configure Sentry DSN
- [ ] Test error reporting

```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=env('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False,
)
```

---

## 🗄️ Database Migrations

### 13. **Migration Safety**

> [!WARNING]
> Always backup your database before running migrations in production!

- [ ] Test migrations on staging environment first
- [ ] Backup production database
- [ ] Run migrations during low-traffic periods
- [ ] Have rollback plan ready
- [ ] Check for migration conflicts

**Deployment migration commands:**
```bash
# Backup database first!
python manage.py migrate --check
python manage.py migrate --plan
python manage.py migrate
```

---

## 🌐 Infrastructure

### 14. **Web Server (Nginx/Apache)**

- [ ] Configure reverse proxy to Gunicorn/uWSGI
- [ ] Enable HTTPS with SSL certificate (Let's Encrypt)
- [ ] Configure rate limiting
- [ ] Set up load balancing (if needed)
- [ ] Configure proper timeout values

**Example Nginx config:**
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/staticfiles/;
    }
}
```

---

### 15. **SSL/TLS Certificate**

- [ ] Obtain SSL certificate (Let's Encrypt recommended)
- [ ] Configure auto-renewal
- [ ] Test SSL configuration (SSL Labs)
- [ ] Enable HTTP/2

```bash
# Let's Encrypt with Certbot
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## 🧪 Pre-Deployment Testing

### 16. **Testing Checklist**

- [ ] Run all unit tests: `python manage.py test`
- [ ] Check for security issues: `python manage.py check --deploy`
- [ ] Test API endpoints on staging
- [ ] Load testing (Apache Bench, Locust)
- [ ] Test database backups and restoration
- [ ] Verify email sending works
- [ ] Test payment processing (if applicable)

---

## 📋 Deployment Steps

### 17. **Standard Deployment Process**

```bash
# 1. Pull latest code
git pull origin main

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install/update dependencies
pip install -r requirements.txt

# 4. Collect static files
python manage.py collectstatic --noinput

# 5. Run migrations
python manage.py migrate

# 6. Restart application server
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# 7. Check logs
tail -f /var/log/gunicorn/error.log
```

---

## 🔄 Post-Deployment

### 18. **Post-Deployment Verification**

- [ ] Verify application is accessible
- [ ] Test critical user flows (login, checkout, etc.)
- [ ] Check error logs for issues
- [ ] Monitor performance metrics
- [ ] Verify database connections
- [ ] Test API endpoints
- [ ] Check email notifications

---

## 📦 Dependencies Update

### 19. **requirements.txt for Production**

Update your `requirements.txt` with production dependencies:

```txt
# Core
asgiref==3.11.0
Django==5.2.8
django-environ==0.12.0
djangorestframework==3.16.1
djangorestframework_simplejwt==5.5.1
psycopg2-binary==2.9.11
PyJWT==2.10.1
sqlparse==0.5.3

# Production Server
gunicorn==21.2.0

# Security & CORS
django-cors-headers==4.3.1

# Static Files
whitenoise==6.6.0

# Caching
django-redis==5.4.0
redis==5.0.1

# Monitoring
sentry-sdk==1.39.1

# Storage (if using S3)
# django-storages==1.14.2
# boto3==1.34.14
```

---

## 🚨 Emergency Procedures

### 20. **Rollback Plan**

> [!CAUTION]
> Have a rollback plan ready before deploying!

**Quick Rollback Steps:**
```bash
# 1. Revert to previous git commit
git revert HEAD
git push origin main

# 2. Restore database backup (if migrations were run)
psql -U username -d dbname < backup.sql

# 3. Redeploy previous version
# Follow deployment steps with previous code

# 4. Restart services
sudo systemctl restart gunicorn nginx
```

---

## ✅ Final Checklist

Before going live, verify ALL of these:

- [ ] `DEBUG = False`
- [ ] `ALLOWED_HOSTS` configured
- [ ] Strong `SECRET_KEY` in production
- [ ] Database backups automated
- [ ] SSL certificate installed and auto-renewing
- [ ] CORS properly configured
- [ ] Static files served correctly
- [ ] Media files storage configured
- [ ] Error tracking (Sentry) working
- [ ] Logging configured
- [ ] Monitoring set up
- [ ] All tests passing
- [ ] Security check passes: `python manage.py check --deploy`
- [ ] Load testing completed
- [ ] Rollback plan documented
- [ ] Team notified of deployment

---

## 📚 Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [Django Security Best Practices](https://docs.djangoproject.com/en/5.2/topics/security/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Let's Encrypt](https://letsencrypt.org/)
- [SSL Labs Test](https://www.ssllabs.com/ssltest/)

---

**Last Updated:** 2025-11-25
