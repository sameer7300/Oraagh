from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, AbandonedCart

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at', 'get_total_items']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    inlines = [CartItemInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_price', 'subtotal']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'get_tracking_display', 'total', 'created_at']
    list_filter = ['status', 'payment_status', 'courier_name', 'created_at']
    search_fields = ['order_number', 'user__username', 'billing_email', 'tracking_number']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    def save_model(self, request, obj, form, change):
        """Override save to track status changes and send emails"""
        if change:  # Only for existing orders
            # Get the original object from database
            try:
                original = Order.objects.get(pk=obj.pk)
                obj._original_status = original.status
            except Order.DoesNotExist:
                obj._original_status = obj.status
        
        super().save_model(request, obj, form, change)
        
        # Add success message for admin
        if change and hasattr(obj, '_original_status') and obj._original_status != obj.status:
            self.message_user(
                request, 
                f"Order {obj.order_number} status changed to {obj.get_status_display()}. "
                f"Email notification sent to {obj.billing_email}."
            )
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_method', 'payment_status')
        }),
        ('Billing Information', {
            'fields': ('billing_name', 'billing_email', 'billing_phone', 'billing_address',
                      'billing_city', 'billing_state', 'billing_zip', 'billing_country')
        }),
        ('Shipping Information', {
            'fields': ('shipping_name', 'shipping_address', 'shipping_city',
                      'shipping_state', 'shipping_zip', 'shipping_country')
        }),
        ('Tracking Information', {
            'fields': ('tracking_number', 'courier_name', 'courier_contact', 'tracking_url'),
            'description': 'Add tracking details when order is processing or shipped'
        }),
        ('Order Totals', {
            'fields': ('subtotal', 'tax', 'shipping_cost', 'total')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(AbandonedCart)
class AbandonedCartAdmin(admin.ModelAdmin):
    list_display = ['user', 'stage', 'cart_total', 'last_activity_at', 'cart_reminder_sent', 'checkout_reminder_sent', 'is_recovered']
    list_filter = ['stage', 'cart_reminder_sent', 'checkout_reminder_sent', 'is_recovered', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['cart_items_snapshot', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Cart Information', {
            'fields': ('user', 'stage', 'cart_total', 'cart_items_snapshot')
        }),
        ('Tracking', {
            'fields': ('cart_created_at', 'last_activity_at', 'checkout_started_at')
        }),
        ('Email Status', {
            'fields': ('cart_reminder_sent', 'cart_reminder_sent_at', 'checkout_reminder_sent', 'checkout_reminder_sent_at')
        }),
        ('Recovery Status', {
            'fields': ('is_recovered', 'recovered_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
