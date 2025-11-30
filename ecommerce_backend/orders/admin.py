from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('extended_price',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user_type', 'email_display', 'status', 
        'total_price', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'is_guest', 'payment_method']
    search_fields = [
        'id', 'user__email', 'guest_email', 'first_name', 'last_name', 'email'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at', 'total_price']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Info', {
            'fields': ('id', 'status', 'created_at', 'updated_at')
        }),
        ('User Info', {
            'fields': ('user', 'is_guest', 'session_key')
        }),
        ('Contact Info', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'guest_email')
        }),
        ('Shipping Address', {
            'fields': (
                'shipping_address', 'shipping_address_line_2',
                'shipping_city', 'shipping_state',
                'shipping_postal_code', 'shipping_country'
            )
        }),
        ('Payment Info', {
            'fields': ('payment_method', 'payment_intent_id', 'paid_at', 'total_price')
        }),
    )

    def email_display(self, obj):
        return obj.guest_email if obj.is_guest else (obj.user.email if obj.user else '-')
    email_display.short_description = 'Email'

    def user_type(self, obj):
        return "Guest" if obj.is_guest else "Registered"
    user_type.short_description = 'User Type'
    user_type.admin_order_field = 'is_guest'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'extended_price']
    search_fields = ['order__id', 'product__name']
