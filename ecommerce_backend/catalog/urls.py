from django.urls import path
from .views import CategoryListView, ProductListCreateView, ProductDetail, CategoryDetail

app_name = 'catalog'

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<uuid:id>/', ProductDetail.as_view(), name='product-detail'),
    path('categories/<str:slug>/', CategoryDetail.as_view(), name='category-detail'),
]
