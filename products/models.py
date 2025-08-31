from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import RegexValidator

class ProductCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Product Categories'

class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    category = models.ForeignKey(ProductCategory, related_name='products', on_delete=models.SET_NULL, null=True, blank=True)
    sku = models.CharField(
        max_length=12,
        unique=True,
        validators=[
            RegexValidator(
                regex='^[0-9]{8,12}$',
                message='SKU must be an 8 to 12 digit number.',
                code='invalid_sku'
            )
        ],
        blank=True,
        null=True, # Allows products to be created without an SKU
        help_text="Must be a unique 8-12 digit number."
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tax_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00,
        help_text="Tax percentage (e.g., 18.00 for 18%)"
    )
    stock_quantity = models.PositiveIntegerField(default=0)
    PRODUCT_TYPE_CHOICES = [
        ('PASHMINA', 'Pashmina'),
        ('CASHMERE', 'Cashmere'),
        ('WOOL', 'Wool'),
        ('SILK', 'Silk'),
        ('COTTON', 'Cotton'),
        ('BLEND', 'Blend'),
        ('OTHER', 'Other'),
    ]
    CONDITION_CHOICES = [
        ('NEW', 'New'),
        ('EXCELLENT', 'Excellent'),
        ('VERY_GOOD', 'Very Good'),
        ('GOOD', 'Good'),
        ('FAIR', 'Fair'),
        ('HANDMADE', 'Handmade'),
        ('VINTAGE', 'Vintage'),
    ]
    product_type = models.CharField(max_length=100, choices=PRODUCT_TYPE_CHOICES, default='OTHER', help_text="Type of shawl material")
    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES, default='NEW')

    weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Weight of the product", blank=True, null=True)
    WEIGHT_UNIT_CHOICES = (
        ('g', 'grams'),
        ('kg', 'kilograms'),
        ('oz', 'ounces'),
    )
    weight_unit = models.CharField(max_length=10, choices=WEIGHT_UNIT_CHOICES, default='kg')
    
    # E-commerce fields
    is_featured = models.BooleanField(default=False, help_text="Mark as featured product")
    is_active = models.BooleanField(default=True, help_text="Product is available for purchase")
    origin_country = models.CharField(max_length=100, blank=True, help_text="Country of origin")
    brand = models.CharField(max_length=100, blank=True, help_text="Product brand")
    condition = models.CharField(max_length=50, choices=[
        ('new', 'New'),
        ('used', 'Used - Like New'),
        ('vintage', 'Vintage'),
        ('antique', 'Antique'),
        ('refurbished', 'Refurbished')
    ], default='new')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})

    def get_tax_amount(self):
        """Calculate tax amount based on price and tax percentage"""
        if self.price and self.tax_percentage:
            return (self.price * self.tax_percentage) / 100
        return 0
    
    def get_price_with_tax(self):
        """Get total price including tax"""
        if self.price:
            return self.price + self.get_tax_amount()
        return 0
    
    def get_price_display(self):
        """Get formatted price display"""
        if self.price:
            return f"PKR {self.price:,.2f}"
        return "Price not set"
    
    def get_price_with_tax_display(self):
        """Get formatted price with tax display"""
        total = self.get_price_with_tax()
        if total:
            return f"PKR {total:,.2f}"
        return "Price not set"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            num = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{num}'
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']

class ProductMedia(models.Model):
    product = models.ForeignKey(Product, related_name='media', on_delete=models.CASCADE)
    media_file = models.FileField(upload_to='product_media/')
    is_video = models.BooleanField(default=False)
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Media for {self.product.name}"

class Review(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    author = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, blank=True, null=True)
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.author} for {self.product.name}'

    class Meta:
        ordering = ['-created_at']

class DealRequest(models.Model):
    STATUS_CHOICES = (
        ('New', 'New'),
        ('Contacted', 'Contacted'),
        ('Closed', 'Closed'),
    )

    product = models.ForeignKey(Product, related_name='deal_requests', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='New')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Deal request from {self.name} for {self.product.name}'
