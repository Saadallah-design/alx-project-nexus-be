# Swagger API Documentation Setup Guide

This guide explains how to add comprehensive API documentation to your Django REST Framework project using Swagger/OpenAPI.

---

## 📦 Installation

### 1. Install drf-spectacular

```bash
pip install drf-spectacular
```

### 2. Update requirements.txt

```bash
pip freeze > requirements.txt
```

---

## ⚙️ Configuration

### 1. Update `settings.py`

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... other apps
    'drf_spectacular',
    'rest_framework',
    # ... your apps
]
```

Configure REST Framework to use drf-spectacular:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # Add this for Swagger schema generation
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
```

Add drf-spectacular settings:

```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'E-Commerce Backend API',
    'DESCRIPTION': '''
    Complete API documentation for the E-Commerce Backend system.
    
    ## Features
    - 🛒 Cart Management
    - 📦 Product Catalog
    - 👤 User Authentication (JWT)
    - 🛍️ Order Processing
    - 📧 Email Notifications (Celery)
    
    ## Authentication
    This API uses JWT (JSON Web Tokens) for authentication.
    
    To authenticate:
    1. Obtain tokens via `/api/users/token/` endpoint
    2. Include the access token in requests: `Authorization: Bearer <access_token>`
    3. Refresh expired tokens via `/api/users/token/refresh/`
    
    ## Guest Checkout
    Guest users can checkout without authentication using `/api/orders/guest-checkout/`
    ''',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api',
    'SERVERS': [
        {'url': 'http://localhost:8000', 'description': 'Development server'},
        {'url': 'https://api.yourdomain.com', 'description': 'Production server'},
    ],
    'TAGS': [
        {'name': 'Authentication', 'description': 'User registration, login, and token management'},
        {'name': 'Products', 'description': 'Product catalog and search'},
        {'name': 'Cart', 'description': 'Shopping cart operations'},
        {'name': 'Orders', 'description': 'Order creation and management'},
        {'name': 'Categories', 'description': 'Product categories'},
    ],
    # Security schemes
    'SECURITY': [{'bearerAuth': []}],
    'APPEND_COMPONENTS': {
        'securitySchemes': {
            'bearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            }
        }
    },
}
```

### 2. Update URLs

In `ecommerce_backend/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/users/', include('users.urls')),
    path('api/catalog/', include('catalog.urls')),
    path('api/orders/', include('orders.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 📝 Documenting Your APIs

### 1. Document Views with Docstrings

```python
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

class ProductListView(generics.ListAPIView):
    """
    List all available products with filtering and search capabilities.
    
    Products can be filtered by:
    - Category
    - Price range
    - Availability status
    - Featured/New/Best Seller flags
    
    Use the search parameter to search by product name or description.
    """
    queryset = Product.objects.filter(is_available=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
```

### 2. Use @extend_schema Decorator

For more detailed documentation:

```python
@extend_schema(
    tags=['Products'],
    summary='List all products',
    description='Retrieve a list of all available products with optional filtering',
    parameters=[
        OpenApiParameter(
            name='category',
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.QUERY,
            description='Filter by category ID',
            required=False,
        ),
        OpenApiParameter(
            name='search',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Search products by name or description',
            required=False,
        ),
        OpenApiParameter(
            name='min_price',
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description='Minimum price filter',
            required=False,
        ),
        OpenApiParameter(
            name='max_price',
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description='Maximum price filter',
            required=False,
        ),
    ],
    examples=[
        OpenApiExample(
            'Product List Response',
            value={
                'count': 10,
                'next': 'http://localhost:8000/api/catalog/products/?page=2',
                'previous': None,
                'results': [
                    {
                        'id': '123e4567-e89b-12d3-a456-426614174000',
                        'name': 'Traditional Jellaba',
                        'description': 'Authentic Moroccan jellaba',
                        'base_price': '299.99',
                        'sale_price': '249.99',
                        'stock_quantity': 15,
                        'category': {
                            'id': '123e4567-e89b-12d3-a456-426614174001',
                            'name': 'Traditional Wear'
                        }
                    }
                ]
            },
            response_only=True,
        )
    ],
    responses={
        200: ProductSerializer(many=True),
        400: OpenApiTypes.OBJECT,
    }
)
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_available=True)
    serializer_class = ProductSerializer
```

### 3. Document Checkout Endpoints

Example for the checkout view:

```python
@extend_schema(
    tags=['Orders'],
    summary='Checkout - Create order for authenticated user',
    description='''
    Convert the user's cart to a pending order.
    
    **Process:**
    1. Retrieves active cart for authenticated user
    2. Validates cart has items
    3. Saves shipping information
    4. Changes order status from CART to PENDING
    5. Sends order confirmation email asynchronously via Celery
    
    **Email Notification:**
    - Email is sent in the background (async)
    - User receives confirmation within 1-2 minutes
    - Check spam folder if not received
    
    **Next Steps:**
    After successful checkout, proceed to payment using the returned order_id.
    ''',
    request=CheckoutSerializer,
    examples=[
        OpenApiExample(
            'Checkout Request',
            value={
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'phone_number': '+1234567890',
                'shipping_address': '123 Main Street',
                'shipping_address_line_2': 'Apt 4B',
                'shipping_city': 'New York',
                'shipping_state': 'NY',
                'shipping_postal_code': '10001',
                'shipping_country': 'USA'
            },
            request_only=True,
        ),
        OpenApiExample(
            'Checkout Success Response',
            value={
                'message': 'Order placed. Proceed to payment.',
                'order_id': '550e8400-e29b-41d4-a716-446655440000',
                'total': 299.99
            },
            response_only=True,
        )
    ],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
                'order_id': {'type': 'string', 'format': 'uuid'},
                'total': {'type': 'number', 'format': 'float'}
            }
        },
        400: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
    }
)
class CheckoutView(generics.GenericAPIView):
    # ... view implementation
```

### 4. Document Authentication Endpoints

```python
@extend_schema(
    tags=['Authentication'],
    summary='Obtain JWT token pair',
    description='Login with email and password to receive access and refresh tokens',
    request={
        'type': 'object',
        'properties': {
            'email': {'type': 'string', 'format': 'email'},
            'password': {'type': 'string', 'format': 'password'}
        },
        'required': ['email', 'password']
    },
    examples=[
        OpenApiExample(
            'Login Request',
            value={
                'email': 'user@example.com',
                'password': 'securepassword123'
            },
            request_only=True,
        ),
        OpenApiExample(
            'Token Response',
            value={
                'access': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
                'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGc...'
            },
            response_only=True,
        )
    ],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'access': {'type': 'string'},
                'refresh': {'type': 'string'}
            }
        },
        401: OpenApiTypes.OBJECT,
    }
)
```

---

## 🎨 Customizing Serializers for Better Docs

Add help text to serializer fields:

```python
class CheckoutSerializer(serializers.Serializer):
    first_name = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Customer first name'
    )
    last_name = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Customer last name'
    )
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        help_text='''Email address for order confirmation.
        - For authenticated users: Optional - will fallback to user account email if not provided
        - For guest users: Recommended - needed to receive order confirmation email
        '''
    )
    phone_number = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Contact phone number'
    )
    shipping_address = serializers.CharField(
        required=True,
        help_text='Street address (required)'
    )
    shipping_city = serializers.CharField(
        required=True,
        help_text='City name (required)'
    )
    shipping_postal_code = serializers.CharField(
        required=True,
        help_text='Postal/ZIP code (required)'
    )
    shipping_country = serializers.CharField(
        default='Morocco',
        help_text='Country name (defaults to Morocco)'
    )
```

---

## 📧 Email Handling for Guest vs Authenticated Users

### Understanding Email Field Behavior

The email field in checkout endpoints behaves differently based on user authentication status:

#### **Authenticated Users (Logged In)**

```python
@extend_schema(
    tags=['Orders'],
    summary='Checkout for authenticated users',
    description='''
    **Email Handling:**
    - Email field is OPTIONAL in request
    - If provided: Uses the email from request
    - If empty/null: Automatically uses user's account email (user.email)
    - Order confirmation email sent to whichever email is used
    
    **Example Scenarios:**
    1. User provides email in request → Uses that email
    2. User omits email field → Uses account email (john@example.com)
    3. User sends empty string → Uses account email as fallback
    ''',
)
```

**Request Example (with email):**
```json
{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.alternative@example.com",  // ← Uses this
    "shipping_address": "123 Main St",
    "shipping_city": "New York",
    "shipping_postal_code": "10001",
    "shipping_country": "USA"
}
```

**Request Example (without email):**
```json
{
    "first_name": "John",
    "last_name": "Doe",
    // email not included → Uses user.email from authentication
    "shipping_address": "123 Main St",
    "shipping_city": "New York",
    "shipping_postal_code": "10001",
    "shipping_country": "USA"
}
```

#### **Guest Users (Not Logged In)**

```python
@extend_schema(
    tags=['Orders'],
    summary='Guest checkout (no authentication required)',
    description='''
    **Email Handling:**
    - Email field is OPTIONAL but RECOMMENDED
    - If provided: Order confirmation email sent to this address
    - If empty/null: Order created but NO email sent (user won't receive confirmation)
    - Email saved to both order.email and order.guest_email fields
    
    **Best Practice:**
    Always include email for guest checkout to ensure customers receive their order confirmation!
    
    **Example Scenarios:**
    1. Guest provides email → Receives order confirmation ✅
    2. Guest omits email → Order created but no email sent ⚠️
    ''',
)
```

**Request Example (with email - RECOMMENDED):**
```json
{
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane@example.com",  // ← Recommended for confirmation
    "phone_number": "+1234567890",
    "shipping_address": "456 Oak Ave",
    "shipping_city": "Los Angeles",
    "shipping_postal_code": "90001",
    "shipping_country": "USA"
}
```

**Request Example (without email - NOT RECOMMENDED):**
```json
{
    "first_name": "Jane",
    "last_name": "Smith",
    // email omitted → No confirmation email sent ⚠️
    "phone_number": "+1234567890",
    "shipping_address": "456 Oak Ave",
    "shipping_city": "Los Angeles",
    "shipping_postal_code": "90001",
    "shipping_country": "USA"
}
```

### Backend Email Logic

Here's how the backend determines which email to use:

#### **Authenticated Checkout (`/api/orders/checkout/`)**

```python
# Backend logic
cart.email = serializer.validated_data.get('email', '') or request.user.email

# Priority:
# 1. Email from request body (if provided)
# 2. User's account email (fallback)

# Email task trigger
email_to_use = cart.email or request.user.email
if email_to_use:
    send_order_confirmation_email.delay(str(cart.id))
```

#### **Guest Checkout (`/api/orders/guest-checkout/`)**

```python
# Backend logic
email_value = serializer.validated_data.get('email', '')
cart.guest_email = email_value
cart.email = email_value

# Priority:
# 1. Email from request body (if provided)
# 2. No fallback - email will be empty if not provided

# Email task trigger
email_to_use = cart.email or cart.guest_email
if email_to_use:  # Only sends if email provided
    send_order_confirmation_email.delay(str(cart.id))
```

### Frontend Implementation Examples

#### **For Authenticated Users**

```typescript
// Option 1: Include user's email explicitly
const checkoutPayload = {
    email: user.email,  // From user profile
    first_name: formData.firstName,
    // ... other fields
};

// Option 2: Omit email, backend will use account email
const checkoutPayload = {
    // email not included - backend uses authenticated user's email
    first_name: formData.firstName,
    // ... other fields
};

// Both work! Backend handles the fallback
await checkoutApi.createOrder(checkoutPayload);
```

#### **For Guest Users**

```typescript
// ALWAYS include email for guest checkout
const checkoutPayload = {
    email: formData.email,  // ← Required for confirmation email
    first_name: formData.firstName,
    last_name: formData.lastName,
    // ... other fields
};

// Validate email before submission
if (!checkoutPayload.email) {
    alert('Email is required to receive order confirmation');
    return;
}

await checkoutApi.createGuestOrder(checkoutPayload);
```

### API Response Differences

#### **Authenticated Checkout Response**

```json
{
    "message": "Order placed. Proceed to payment.",
    "order_id": "550e8400-e29b-41d4-a716-446655440000",
    "total": 299.99
    // Note: email not included in response (user is authenticated)
}
```

#### **Guest Checkout Response**

```json
{
    "message": "Order placed successfully.",
    "order_id": "660e8400-e29b-41d4-a716-446655440001",
    "total": 149.99,
    "email": "guest@example.com"  // ← Confirms email used
}
```

### Documentation Examples for Swagger

```python
# Authenticated Checkout Example
@extend_schema(
    examples=[
        OpenApiExample(
            'With Custom Email',
            value={
                'email': 'custom@example.com',
                'first_name': 'John',
                'shipping_address': '123 Main St',
                'shipping_city': 'NYC',
                'shipping_postal_code': '10001',
                'shipping_country': 'USA'
            },
            request_only=True,
        ),
        OpenApiExample(
            'Without Email (Uses Account Email)',
            value={
                'first_name': 'John',
                'shipping_address': '123 Main St',
                'shipping_city': 'NYC',
                'shipping_postal_code': '10001',
                'shipping_country': 'USA'
            },
            request_only=True,
        )
    ],
)

# Guest Checkout Example
@extend_schema(
    examples=[
        OpenApiExample(
            'Guest with Email (Recommended)',
            value={
                'email': 'guest@example.com',  # ← Include this!
                'first_name': 'Jane',
                'shipping_address': '456 Oak Ave',
                'shipping_city': 'LA',
                'shipping_postal_code': '90001',
                'shipping_country': 'USA'
            },
            request_only=True,
        )
    ],
)
```

### Key Takeaways

| User Type | Email Field | Behavior | Email Sent? |
|-----------|-------------|----------|-------------|
| **Authenticated** | Provided | Uses provided email | ✅ Yes |
| **Authenticated** | Empty/Omitted | Uses user.email | ✅ Yes |
| **Guest** | Provided | Uses provided email | ✅ Yes |
| **Guest** | Empty/Omitted | No email available | ❌ No |

### Best Practices

1. **For Authenticated Users:**
   - Frontend can omit email field - backend will handle it
   - Or include it explicitly for clarity
   - User will always receive confirmation (uses account email)

2. **For Guest Users:**
   - ALWAYS validate and include email in request
   - Show clear message: "Email required for order confirmation"
   - Backend won't send email if not provided

3. **User Experience:**
   - Show email input field for both user types
   - Pre-fill with account email for authenticated users
   - Require email for guest users
   - Display message: "Confirmation email will be sent to: {email}"

---

## 🚀 Accessing Documentation

After setup, access your API documentation at:

### Swagger UI (Interactive)
```
http://localhost:8000/api/docs/
```
- Interactive API explorer
- Try out endpoints directly
- See request/response examples
- Test authentication

### ReDoc (Alternative)
```
http://localhost:8000/api/redoc/
```
- Clean, responsive design
- Better for reading
- No interactive features

### OpenAPI Schema (JSON)
```
http://localhost:8000/api/schema/
```
- Raw OpenAPI 3.0 schema
- Use for client generation
- Import into Postman/Insomnia

---

## 📋 Complete Example: Document All Checkout Endpoints

### In `orders/views.py`:

```python
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

class CheckoutView(generics.GenericAPIView):
    @extend_schema(
        tags=['Orders'],
        summary='Checkout for authenticated users',
        description='Convert cart to order and send email confirmation',
        request=CheckoutSerializer,
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT}
    )
    def post(self, request):
        # ... implementation

class GuestCheckoutView(generics.GenericAPIView):
    @extend_schema(
        tags=['Orders'],
        summary='Guest checkout (no authentication required)',
        description='Create order for guest users without account',
        request=GuestCheckoutSerializer,
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT}
    )
    def post(self, request):
        # ... implementation

class CartView(generics.GenericAPIView):
    @extend_schema(
        tags=['Cart'],
        summary='Get current user cart',
        description='Retrieve active shopping cart for authenticated user',
        responses={200: OrderSerializer, 404: OpenApiTypes.OBJECT}
    )
    def get(self, request):
        # ... implementation

class AddToCartView(generics.GenericAPIView):
    @extend_schema(
        tags=['Cart'],
        summary='Add item to cart',
        description='Add a product to the shopping cart or update quantity',
        request={
            'type': 'object',
            'properties': {
                'product_id': {'type': 'string', 'format': 'uuid'},
                'quantity': {'type': 'integer', 'minimum': 1}
            },
            'required': ['product_id', 'quantity']
        },
        responses={200: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT}
    )
    def post(self, request):
        # ... implementation
```

---

## 🔐 Testing Authentication in Swagger

### 1. Obtain Token
1. Navigate to `/api/docs/`
2. Find the `/api/users/token/` endpoint
3. Click "Try it out"
4. Enter credentials
5. Execute
6. Copy the `access` token from response

### 2. Authorize Requests
1. Click the "Authorize" button (🔓 icon) at the top
2. Enter: `Bearer <your_access_token>`
3. Click "Authorize"
4. All subsequent requests will include the token

---

## 🎯 Best Practices

### 1. Consistent Tag Usage
Group related endpoints:
```python
tags=['Orders']        # All order-related endpoints
tags=['Products']      # All product endpoints
tags=['Authentication'] # Login/register endpoints
```

### 2. Detailed Descriptions
Include:
- What the endpoint does
- Required vs optional parameters
- Expected behavior
- Side effects (like sending emails)
- Next steps in the workflow

### 3. Provide Examples
Always include request/response examples:
```python
examples=[
    OpenApiExample('Success Case', value={...}),
    OpenApiExample('Error Case', value={...}, status_codes=['400']),
]
```

### 4. Document Error Responses
```python
responses={
    200: SuccessSerializer,
    400: {'description': 'Bad request - invalid data'},
    401: {'description': 'Unauthorized - token missing or invalid'},
    404: {'description': 'Resource not found'},
}
```

### 5. Use Help Text in Serializers
```python
field = serializers.CharField(
    help_text='Clear description of what this field is for'
)
```

---

## 📦 Production Considerations

### 1. Disable Swagger in Production (Optional)

```python
# settings.py
if not DEBUG:
    SPECTACULAR_SETTINGS['SERVE_INCLUDE_SCHEMA'] = False
```

Or conditionally include URLs:

```python
# urls.py
if settings.DEBUG:
    urlpatterns += [
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    ]
```

### 2. Update Server URLs

```python
SPECTACULAR_SETTINGS = {
    'SERVERS': [
        {'url': 'https://api.yourproduction.com', 'description': 'Production'},
        {'url': 'https://staging.api.yourproduction.com', 'description': 'Staging'},
        {'url': 'http://localhost:8000', 'description': 'Local Development'},
    ],
}
```

---

## 🧪 Verify Setup

Run these commands to verify:

```bash
# Generate schema (should work without errors)
python manage.py spectacular --color --file schema.yml

# Check for warnings
python manage.py spectacular --validate

# Run development server
python manage.py runserver
```

Then visit:
- http://localhost:8000/api/docs/ (Should show Swagger UI)
- http://localhost:8000/api/redoc/ (Should show ReDoc)
- http://localhost:8000/api/schema/ (Should return OpenAPI JSON)

---

## 📚 Additional Resources

- [drf-spectacular Documentation](https://drf-spectacular.readthedocs.io/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [ReDoc](https://redocly.com/docs/redoc/)

---

## ✅ Checklist

- [ ] Install drf-spectacular
- [ ] Update settings.py with SPECTACULAR_SETTINGS
- [ ] Add REST_FRAMEWORK['DEFAULT_SCHEMA_CLASS']
- [ ] Update urls.py with documentation routes
- [ ] Add @extend_schema decorators to views
- [ ] Add help_text to serializer fields
- [ ] Test Swagger UI at /api/docs/
- [ ] Test ReDoc at /api/redoc/
- [ ] Verify authentication flow works in Swagger
- [ ] Add examples for all major endpoints
- [ ] Document error responses

---

## 🎉 Result

After following this guide, you'll have:
- ✅ Interactive API documentation
- ✅ Automatic schema generation
- ✅ Try-it-out functionality
- ✅ JWT authentication support in docs
- ✅ Request/response examples
- ✅ Clean, professional API docs

Your frontend team and API consumers will have complete, interactive documentation to work with! 🚀
