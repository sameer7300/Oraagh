from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

# Create your models here.

class DeliveryCharge(models.Model):
    """Model to manage delivery charges that can be configured from admin"""
    
    DELIVERY_TYPE_CHOICES = [
        ('standard', 'Standard Delivery'),
        ('express', 'Express Delivery'),
        ('overnight', 'Overnight Delivery'),
        ('free', 'Free Delivery'),
    ]
    
    name = models.CharField(max_length=100, help_text="Display name for delivery option")
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_TYPE_CHOICES, default='standard')
    charge = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Delivery charge amount"
    )
    min_order_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Minimum order value for this delivery option"
    )
    max_order_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Maximum order value for this delivery option (leave blank for no limit)"
    )
    estimated_days = models.PositiveIntegerField(
        default=3,
        help_text="Estimated delivery days"
    )
    is_active = models.BooleanField(default=True, help_text="Whether this delivery option is available")
    is_default = models.BooleanField(default=False, help_text="Default delivery option")
    description = models.TextField(blank=True, help_text="Additional description for delivery option")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['charge', 'estimated_days']
        verbose_name = "Delivery Charge"
        verbose_name_plural = "Delivery Charges"
    
    def __str__(self):
        return f"{self.name} - PKR {self.charge}"
    
    def save(self, *args, **kwargs):
        # Ensure only one default delivery option
        if self.is_default:
            DeliveryCharge.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_default(cls):
        """Get the default delivery option"""
        return cls.objects.filter(is_active=True, is_default=True).first()
    
    @classmethod
    def get_available_for_order_value(cls, order_value):
        """Get available delivery options for a given order value"""
        queryset = cls.objects.filter(is_active=True, min_order_value__lte=order_value)
        return queryset.filter(
            models.Q(max_order_value__isnull=True) | 
            models.Q(max_order_value__gte=order_value)
        )
    
    def is_available_for_order_value(self, order_value):
        """Check if this delivery option is available for given order value"""
        if not self.is_active:
            return False
        if order_value < self.min_order_value:
            return False
        if self.max_order_value and order_value > self.max_order_value:
            return False
        return True
