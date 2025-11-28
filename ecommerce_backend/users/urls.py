from django.urls import path
from . import views
# from .views import UserRegistrationView, UserProfileView

app_name = 'users'

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),

    # User Profile View | Private EndPoint (Authenticated Users Only)
    path('me/', views.UserProfileView.as_view(), name='user-profile'), 
]