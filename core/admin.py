from django.contrib import admin
from .models import DeliveryCharge

# Register your models here.

@admin.register(DeliveryCharge)
class DeliveryChargeAdmin(admin.ModelAdmin):
    list_display = ['name', 'delivery_type', 'charge', 'min_order_value', 'max_order_value', 'estimated_days', 'is_active', 'is_default']
    list_filter = ['delivery_type', 'is_active', 'is_default', 'estimated_days']
    search_fields = ['name', 'description']
    list_editable = ['charge', 'is_active', 'is_default']
    ordering = ['charge', 'estimated_days']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'delivery_type', 'description')
        }),
        ('Pricing', {
            'fields': ('charge', 'min_order_value', 'max_order_value')
        }),
        ('Settings', {
            'fields': ('estimated_days', 'is_active', 'is_default')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Ensure only one default delivery option
        if obj.is_default:
            DeliveryCharge.objects.filter(is_default=True).exclude(pk=obj.pk).update(is_default=False)
        super().save_model(request, obj, form, change)
