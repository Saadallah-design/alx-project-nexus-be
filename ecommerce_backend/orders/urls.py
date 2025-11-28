from django.urls import path
from .views import CartRetrieveView, OrderItemManageView

app_name = 'orders'

urlpatterns = [
    path('', CartRetrieveView.as_view(), name='cart-detail'),
    path('items/', OrderItemManageView.as_view(), name='cart-items'),
]
