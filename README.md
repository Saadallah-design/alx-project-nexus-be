# ALX Project Nexus - E-Commerce Backend

A robust Django REST API backend for a modern e-commerce platform, featuring product catalog management, user authentication, order processing, and asynchronous email notifications.

## 🚀 Features

- **Product Catalog Management**
  - RESTful API for products and categories
  - Advanced filtering and search capabilities
  - Custom pagination (12 items per page)
  - Multi-image support for products
  - Stock availability tracking

- **User Authentication & Authorization**
  - JWT-based authentication
  - Custom user model with email/phone
  - Secure password management
  - Token refresh mechanism

- **Order Management**
  - Complete checkout flow
  - Guest and authenticated user orders
  - Order status tracking
  - Shipping information management
  - Payment intent integration ready

- **Asynchronous Task Processing**
  - Celery integration for background tasks
  - Automated order confirmation emails
  - Redis as message broker
  - Scalable worker architecture

- **Production-Ready Deployment**
  - Railway.app deployment configuration
  - PostgreSQL database support
  - Static file serving with WhiteNoise
  - Gunicorn WSGI server
  - Comprehensive security settings

## 📋 Prerequisites

- Python 3.10 or higher
- PostgreSQL (for production)
- Redis (for Celery tasks)
- Virtual environment tool (venv/virtualenv)

## 🛠️ Technology Stack

- **Framework**: Django 5.2.8
- **API**: Django REST Framework 3.16.1
- **Database**: PostgreSQL (production), SQLite (development)
- **Cache/Queue**: Redis
- **Task Queue**: Celery 5.5.3
- **Authentication**: djangorestframework-simplejwt 5.4.2
- **WSGI Server**: Gunicorn 23.0.0
- **Static Files**: WhiteNoise 6.11.0
- **CORS**: django-cors-headers 4.8.0

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Saadallah-design/alx-project-nexus-be.git
cd alx-project-nexus-be
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the `ecommerce_backend` directory:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Development - uses SQLite by default)
# For PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Superuser Creation (optional)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=secure-password
```

### 5. Database Setup

```bash
cd ecommerce_backend
python manage.py migrate
python manage.py createsuperuser  # Or use create_superuser_from_env command
```

### 6. Load Sample Data (Optional)

```bash
python manage.py import_products  # Imports from products_export.json
```

## 🚀 Running the Application

### Development Server

```bash
# Terminal 1: Django development server
cd ecommerce_backend
python manage.py runserver
```

### Celery Worker (for email tasks)

```bash
# Terminal 2: Start Redis (if not running)
redis-server

# Terminal 3: Start Celery worker
cd ecommerce_backend
celery -A ecommerce_backend worker --loglevel=info
```

The API will be available at `http://localhost:8000/`

## 📚 API Documentation

### Base URL
- **Development**: `http://localhost:8000/api/`
- **Production**: `https://web-production-38c24.up.railway.app/api/`

### Main Endpoints

#### Authentication
- `POST /api/users/register/` - User registration
- `POST /api/users/login/` - User login
- `POST /api/users/token/refresh/` - Refresh JWT token
- `GET /api/users/profile/` - Get user profile (authenticated)
- `PUT /api/users/profile/` - Update user profile (authenticated)

#### Catalog
- `GET /api/catalog/products/` - List all products (paginated)
- `GET /api/catalog/products/{id}/` - Get product details
- `GET /api/catalog/categories/` - List all categories
- `GET /api/catalog/categories/{id}/products/` - Products by category

**Query Parameters for Products:**
- `category` - Filter by category ID
- `search` - Search in name/description
- `min_price` / `max_price` - Price range filter
- `available` - Filter available products (true/false)

#### Orders
- `POST /api/orders/checkout/` - Create new order
- `GET /api/orders/` - List user's orders (authenticated)
- `GET /api/orders/{id}/` - Get order details
- `PATCH /api/orders/{id}/` - Update order status

### Example Requests

#### Get Products
```bash
curl -X GET "http://localhost:8000/api/catalog/products/?category=1&min_price=10"
```

#### User Registration
```bash
curl -X POST "http://localhost:8000/api/users/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "securepass123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

#### Create Order
```bash
curl -X POST "http://localhost:8000/api/orders/checkout/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "items": [
      {"product_id": 1, "quantity": 2},
      {"product_id": 3, "quantity": 1}
    ],
    "shipping_address": "123 Main St",
    "shipping_city": "New York",
    "shipping_postal_code": "10001",
    "shipping_country": "USA"
  }'
```

## 🗄️ Database Schema

### Key Models

#### Product
- `name`, `description`, `price`
- `category` (ForeignKey to Category)
- `stock_quantity`, `available`
- `created_at`, `updated_at`
- Database indexes on category and availability

#### Order
- `user` (ForeignKey to User, nullable for guest orders)
- `items` (ManyToMany through OrderItem)
- `total_amount`, `status`
- `shipping_address`, `shipping_city`, `shipping_postal_code`, `shipping_country`
- `payment_intent_id`, `paid_at`
- `session_key`, `guest_email` (for guest orders)

#### CustomUser
- Extends Django's AbstractUser
- Additional fields: `phone_number`
- Email as primary identifier

## 🔧 Management Commands

### Create Superuser from Environment
```bash
python manage.py create_superuser_from_env
```
Reads `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, and `DJANGO_SUPERUSER_PASSWORD` from environment variables.

### Import Products
```bash
python manage.py import_products
```
Imports products from `products_export.json` file.

## 🚢 Deployment

### Railway Deployment

The application is configured for Railway deployment with the following services:

1. **Web Service** (Django + Gunicorn)
2. **Worker Service** (Celery)
3. **PostgreSQL Database**
4. **Redis**

#### Required Environment Variables

```env
# Production Settings
SECRET_KEY=<generated-secret-key>
DEBUG=False
ALLOWED_HOSTS=web-production-38c24.up.railway.app,.railway.app

# Database (automatically set by Railway)
DATABASE_URL=postgresql://...

# Redis (automatically set by Railway)
REDIS_URL=redis://...

# Email Configuration
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Superuser Creation
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=<secure-password>
```

#### Deployment Process

The `Procfile` handles automatic deployment:

```
web: cd ecommerce_backend && python manage.py migrate && python manage.py create_superuser_from_env && gunicorn ecommerce_backend.wsgi --log-file -
worker: cd ecommerce_backend && celery -A ecommerce_backend worker --loglevel=info
```

### Production Checklist

- [x] Set `DEBUG=False`
- [x] Configure `ALLOWED_HOSTS`
- [x] Set `SECURE_PROXY_SSL_HEADER`
- [x] Configure PostgreSQL database
- [x] Set up Redis for Celery
- [x] Configure email backend
- [x] Generate strong `SECRET_KEY`
- [x] Set up static file serving (WhiteNoise)
- [x] Run database migrations
- [x] Create superuser
- [ ] Configure media file storage (S3/Cloudinary)
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test catalog
python manage.py test orders
python manage.py test users
```

## 📁 Project Structure

```
alx-project-nexus-be/
├── ecommerce_backend/          # Django project root
│   ├── catalog/                # Product catalog app
│   │   ├── models.py          # Product, Category, ProductImage models
│   │   ├── views.py           # API views for products
│   │   ├── serializers.py     # DRF serializers
│   │   └── management/        # Custom commands
│   ├── orders/                 # Order management app
│   │   ├── models.py          # Order, OrderItem models
│   │   ├── views.py           # Checkout and order views
│   │   ├── tasks.py           # Celery tasks for emails
│   │   └── serializers.py     # Order serializers
│   ├── users/                  # User authentication app
│   │   ├── models.py          # CustomUser model
│   │   ├── views.py           # Auth endpoints
│   │   └── serializers.py     # User serializers
│   ├── ecommerce_backend/      # Project settings
│   │   ├── settings.py        # Django configuration
│   │   ├── urls.py            # URL routing
│   │   ├── celery.py          # Celery configuration
│   │   └── wsgi.py            # WSGI application
│   └── media/                  # User-uploaded files
├── documentation/              # Project documentation
├── Procfile                    # Railway deployment config
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔐 Security Features

- HTTPS enforcement in production
- Secure cookie settings
- CSRF protection
- SQL injection protection (Django ORM)
- XSS protection
- Password hashing with PBKDF2
- JWT token authentication
- CORS configuration
- Environment-based secrets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is part of the ALX Software Engineering program.

## 📧 Contact

For questions or support, please contact the development team.

## 🙏 Acknowledgments

- ALX Software Engineering Program
- Django and DRF communities
- Railway.app for hosting platform

---

**Live API**: [https://web-production-38c24.up.railway.app](https://web-production-38c24.up.railway.app)

**Admin Panel**: [https://web-production-38c24.up.railway.app/admin/](https://web-production-38c24.up.railway.app/admin/)
