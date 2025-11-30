from django.urls import path
from .views import (
    CartRetrieveView, OrderItemManageView, OrderItemDetailView, 
    CheckoutView, MockPaymentView, OrderListView, OrderDetailView,
    GuestCheckoutView, GuestOrderLookupView, LinkGuestOrdersView
)

app_name = 'orders'

urlpatterns = [
    path('', CartRetrieveView.as_view(), name='cart-detail'),
    path('items/', OrderItemManageView.as_view(), name='cart-items'),
    path('items/<int:pk>/', OrderItemDetailView.as_view(), name='cart-item-detail'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('orders/<uuid:order_id>/pay/', MockPaymentView.as_view(), name='mock-payment'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<uuid:id>/', OrderDetailView.as_view(), name='order-detail'),
    
    # Guest Checkout
    path('guest/checkout/', GuestCheckoutView.as_view(), name='guest-checkout'),
    path('guest/orders/lookup/', GuestOrderLookupView.as_view(), name='guest-order-lookup'),
    path('link-guest-orders/', LinkGuestOrdersView.as_view(), name='link-guest-orders'),

]
