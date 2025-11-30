
from django.contrib import admin
from django.urls import path, include, re_path
from users.views import UserRegistrationView
from django.conf import settings 
from django.conf.urls.static import static

# setting our JWT 
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView, 
)

# Swagger/OpenAPI documentation
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="E-commerce Backend API",
        default_version='v1',
        description="""
        Complete API documentation for the ALX Project Nexus E-commerce Backend.
        
        ## Features
        - **User Authentication**: JWT-based authentication with registration and login
        - **Product Catalog**: Browse products and categories
        - **Shopping Cart**: Manage cart items
        - **Orders**: Place and track orders
        
        ## Authentication
        Most endpoints require JWT authentication. To authenticate:
        1. Register a new account at `/api/auth/register/`
        2. Login at `/api/auth/token/` to get access and refresh tokens
        3. Include the access token in the Authorization header: `Bearer <token>`
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@ecommerce.local"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/catalog/', include('catalog.urls')),
    path('api/auth/', include('users.urls')),
    path('api/cart/', include('orders.urls')),

    # JWT urls
    # these urls are used for authentication and authorization
    # they are prebuilt by the rest_framework_simplejwt package
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),

    # Swagger/OpenAPI documentation endpoints
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='api-docs'),  # Root endpoint shows Swagger UI

    # setting user registration urls
    # path('api/auth/register/', UserRegistrationView.as_view(), name='user_registration'),
]
# SERVING MEDIA IN DEVELOPMENT 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)