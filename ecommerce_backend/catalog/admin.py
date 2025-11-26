from django.contrib import admin
from .models import Category, Product

# Register your models here.

# So, since last time I created the models for catalog and product, I need to register them in the admin.py file
# I will not use the simple registration method, but I will use the django admin interface to manage the models
# since they offer less customization
# admin.site.register(Category)
# admin.site.register(Product)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'base_price',
        'stock_quantity',
        'is_available',
        'is_featured',
    )
    list_filter = ('category', 'is_available', 'is_featured', 'created_at')
    list_editable = ('base_price', 'stock_quantity', 'is_available', 'is_featured')
    search_fields = ('name', 'description')
    ordering = ('name',)