
from pathlib import Path
import environ
from datetime import timedelta


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Initialize environ
# Use BASE_DIR / '.env' to locate the file
env = environ.Env(
    # Set casting and default value for DEBUG
    DEBUG=(bool, False) 
)
# Read the .env file
# This reads the environment variables from the file into the environment
environ.Env.read_env(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'drf_yasg',  # Swagger/OpenAPI documentation
    # users app fro built in
    # 'users',
    'users.apps.UsersConfig',
    'catalog',
    'rest_framework_simplejwt.token_blacklist',
    
    # 'cart',
    'orders',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # MUST be at the top for CORS to work
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ecommerce_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecommerce_backend.wsgi.application'


# Database
# Changing Database from sqlite to PostgreSQL
# Database configuration using the DATABASE_URL
DATABASES = {
    'default': env.db(),
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'ecommerce_db',
#         'USER': 'salah-eddinesaadalla',
#         'PASSWORD': 'postgres',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#  using the custom user model - to define in the users app later.
AUTH_USER_MODEL = 'users.CustomUser'


# Setting the JWT configuration 
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        # Default security setting: only authenticated users can access the API
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    )
}

# simple JWT configuration
# this requires an import of: timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),


    
    'ROTATE_REFRESH_TOKENS': True, #When set to True, if a refresh token is submitted to the TokenRefreshView, a new refresh token will be returned along with the new access token.
    'BLACKLIST_AFTER_ROTATION': True, #When set to True, the old refresh token will be blacklisted after rotation.
    # for the blacklist_after_rotation it requires being added to installed apps: 'rest_framework_simplejwt.token_blacklist',
    'ALGORITHM': 'HS256', #The algorithm used for signing the tokens.
    'SIGNING_KEY': SECRET_KEY, # Uses the secret key we set earlier
    'AUTH_HEADER_TYPES': ('Bearer',),

    # here the user identification settings relate the token back to the custom user in our project which uses UUID as primary key
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}


# CORS Configuration (for development and testing)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]

CORS_ALLOW_CREDENTIALS = True

# Setting img upload path
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ===========================
# EMAIL CONFIGURATION
# ===========================

# Choose email backend based on DEBUG setting
if DEBUG:
    # Development: Print emails to console
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # Production: Send real emails via SMTP
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = env.int('EMAIL_PORT', default=587)
    EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
    EMAIL_HOST_USER = env('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@ecommerce.com')
    SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Optional: For testing real emails in development
# Uncomment these lines and add credentials to .env to test real email sending
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@ecommerce.com')

# Fix for SSL certificate verification issues on macOS
import ssl
EMAIL_SSL_CERTFILE = None
EMAIL_SSL_KEYFILE = None
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


# ===========================
# CELERY CONFIGURATION
# ===========================

# Celery Broker URL (Redis)
CELERY_BROKER_URL = 'redis://localhost:6379/0'

# Celery Result Backend (it works through Redis - stores task results)
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

# Optional: Task routing (advanced I need to read about it more)
# CELERY_TASK_ROUTES = {
#     'orders.tasks.send_order_email': {'queue': 'emails'},
#     'orders.tasks.process_payment': {'queue': 'payments'},
# }