
from django.contrib import admin
from django.urls import path, include
from users.views import UserRegistrationView

# setting our JWT 
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView, 
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/catalog/', include('catalog.urls')),
    path('api/auth/', include('users.urls')),
    path('api/cart/', include('orders.urls')),


    # JWT urls
    # these urls are used for authentication and authorization
    # they are prebuilt by the rest_framework_simplejwt package
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),

    # setting user registration urls
    # path('api/auth/register/', UserRegistrationView.as_view(), name='user_registration'),
]