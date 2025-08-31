from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from django.utils import timezone
from decimal import Decimal

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_total(self):
        """Get total cart value including tax"""
        return sum(item.get_subtotal() for item in self.items.all())
    
    def get_subtotal_without_tax(self):
        """Get cart subtotal without tax"""
        return sum(item.get_subtotal_without_tax() for item in self.items.all())
    
    def get_total_tax(self):
        """Get total tax amount for cart"""
        return sum(item.get_tax_amount() for item in self.items.all())
    
    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())
    
    def __str__(self):
        return f"Cart for {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    def get_subtotal(self):
        """Get subtotal including tax for this cart item"""
        if self.product.price:
            return self.product.get_price_with_tax() * self.quantity
        return Decimal('0.00')
    
    def get_subtotal_without_tax(self):
        """Get subtotal without tax for this cart item"""
        return self.product.price * self.quantity if self.product.price else Decimal('0.00')
    
    def get_tax_amount(self):
        """Get total tax amount for this cart item"""
        if self.product.price:
            return self.product.get_tax_amount() * self.quantity
        return Decimal('0.00')
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    class Meta:
        unique_together = ['cart', 'product']

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Billing Information
    billing_name = models.CharField(max_length=100)
    billing_email = models.EmailField()
    billing_phone = models.CharField(max_length=20)
    billing_address = models.TextField()
    billing_city = models.CharField(max_length=100)
    billing_state = models.CharField(max_length=100)
    billing_zip = models.CharField(max_length=20)
    billing_country = models.CharField(max_length=100)
    
    # Shipping Information (can be same as billing)
    shipping_name = models.CharField(max_length=100)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_zip = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100)
    
    # Order details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment
    payment_method = models.CharField(max_length=50, default='Cash on Delivery')
    payment_status = models.CharField(max_length=20, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Tracking Information
    tracking_number = models.CharField(max_length=100, blank=True, help_text="Tracking number from courier")
    courier_name = models.CharField(max_length=100, blank=True, help_text="Name of courier company")
    courier_contact = models.CharField(max_length=50, blank=True, help_text="Courier contact number")
    tracking_url = models.URLField(blank=True, help_text="URL to track package online")
    
    # Notes
    customer_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_status = self.status
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate unique order number
            import random
            import string
            self.order_number = 'ORD' + ''.join(random.choices(string.digits, k=8))
        super().save(*args, **kwargs)
        # Update original status after save
        self._original_status = self.status
    
    def has_tracking_info(self):
        """Check if order has tracking information"""
        return bool(self.tracking_number and self.courier_name)
    
    def get_tracking_display(self):
        """Get formatted tracking information"""
        if self.has_tracking_info():
            return f"{self.courier_name}: {self.tracking_number}"
        return "Not available"
    
    def __str__(self):
        return f"Order {self.order_number} - {self.user.username}"
    
    class Meta:
        ordering = ['-created_at']

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255)  # Store name in case product is deleted
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        if self.product:
            self.product_name = self.product.name
            self.product_price = self.product.price
        self.subtotal = self.product_price * self.quantity
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quantity} x {self.product_name}"


class AbandonedCart(models.Model):
    STAGE_CHOICES = (
        ('cart', 'Cart Abandoned'),
        ('checkout', 'Checkout Abandoned'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='abandoned_carts')
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='cart')
    cart_items_snapshot = models.JSONField()  # Store cart items as JSON
    cart_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Tracking fields
    cart_created_at = models.DateTimeField()
    last_activity_at = models.DateTimeField()
    checkout_started_at = models.DateTimeField(null=True, blank=True)
    
    # Email tracking
    cart_reminder_sent = models.BooleanField(default=False)
    cart_reminder_sent_at = models.DateTimeField(null=True, blank=True)
    checkout_reminder_sent = models.BooleanField(default=False)
    checkout_reminder_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_recovered = models.BooleanField(default=False)
    recovered_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Abandoned {self.stage} - {self.user.username} - PKR {self.cart_total}"
    
    def get_hours_since_last_activity(self):
        """Get hours since last activity"""
        return (timezone.now() - self.last_activity_at).total_seconds() / 3600
    
    def should_send_cart_reminder(self):
        """Check if cart reminder should be sent (after 2 hours)"""
        return (
            self.stage == 'cart' and
            not self.cart_reminder_sent and
            not self.is_recovered and
            self.get_hours_since_last_activity() >= 2
        )
    
    def should_send_checkout_reminder(self):
        """Check if checkout reminder should be sent (after 1 hour)"""
        return (
            self.stage == 'checkout' and
            not self.checkout_reminder_sent and
            not self.is_recovered and
            self.checkout_started_at and
            (timezone.now() - self.checkout_started_at).total_seconds() / 3600 >= 1
        )
    
    class Meta:
        ordering = ['-updated_at']
