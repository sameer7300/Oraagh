# Developer Guide - Red Sun Mining (Oraagh)

This guide provides detailed information for developers working on the Red Sun Mining e-commerce platform.

## 🏗️ Architecture Overview

### Django Apps Architecture

#### Core App (`core/`)
**Purpose**: Base functionality, home page, and shared components
- **Models**: None (uses other app models)
- **Views**: `home_view()`, `about_view()`, newsletter subscription
- **Templates**: `base.html`, `home.html`, `about.html`
- **Key Features**: Featured products display, category navigation

#### Accounts App (`accounts/`)
**Purpose**: User authentication and profile management
- **Models**: `UserProfile`, `PasswordResetCode`, `EmailVerificationCode`
- **Views**: Registration, login, profile management, password reset
- **Key Features**: 6-digit email verification, role-based access
- **Security**: Custom password validation, rate limiting

#### Products App (`products/`)
**Purpose**: Product catalog and customer interactions
- **Models**: `ProductCategory`, `Product`, `ProductMedia`, `Review`, `DealRequest`
- **Views**: Product listing with filters, product detail, review submission
- **Key Features**: SKU management, tax calculation, media galleries
- **Business Logic**: Price calculations, stock tracking, review moderation

#### Orders App (`orders/`)
**Purpose**: Shopping cart and order processing
- **Models**: `Cart`, `CartItem`, `Order`, `OrderItem`, `AbandonedCart`
- **Views**: Cart management, checkout process, order tracking
- **Key Features**: AJAX cart updates, abandoned cart tracking
- **Automation**: Abandoned cart email reminders

#### Blog App (`blog/`)
**Purpose**: Content management and SEO
- **Models**: `Category`, `Tag`, `Post`
- **Views**: Post listing, detail view with view counting
- **Key Features**: SEO-friendly URLs, related posts, view tracking

#### Newsletter App (`newsletter/`)
**Purpose**: Email marketing and subscriber management
- **Models**: `Subscriber`
- **Views**: Subscription handling, newsletter composition and sending
- **Key Features**: Bulk email sending, subscription management

#### Admin Dashboard App (`admin_dashboard/`)
**Purpose**: Custom admin interface
- **Views**: Dashboard with statistics, CRUD operations for all models
- **Key Features**: Order management, product management, customer analytics
- **Security**: Admin-only access with custom authentication

#### Portfolio App (`portfolio/`)
**Purpose**: Lease and team management
- **Models**: `Lease`, `TeamMember`, `LeaseTeamMember`, `LeaseMedia`
- **Views**: Portfolio display, lease details, PDF generation, mapping
- **Key Features**: Interactive maps with Leaflet.js, PDF export

#### Contact App (`contact/`)
**Purpose**: Customer communication
- **Views**: Contact form handling with email notifications
- **Key Features**: Automated email responses, admin notifications

## 🔧 Development Patterns

### Model Design Patterns

#### Base Model Pattern
```python
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
```

#### Slug Generation Pattern
```python
def save(self, *args, **kwargs):
    if not self.slug:
        self.slug = slugify(self.name)
        # Ensure uniqueness
        counter = 1
        while self.__class__.objects.filter(slug=self.slug).exists():
            self.slug = f"{slugify(self.name)}-{counter}"
            counter += 1
    super().save(*args, **kwargs)
```

#### Price Calculation Pattern
```python
def get_price_with_tax(self):
    """Calculate price including tax."""
    tax_amount = self.price * (self.tax_percentage / 100)
    return self.price + tax_amount

def get_total_price(self):
    """Get total price for quantity."""
    return self.get_price_with_tax() * self.quantity
```

### View Design Patterns

#### Class-Based Views
```python
class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        # Add filtering logic
        return queryset
```

#### AJAX Response Pattern
```python
def ajax_view(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Handle AJAX request
        return JsonResponse({'status': 'success', 'data': data})
    # Handle regular request
    return render(request, 'template.html', context)
```

### Form Design Patterns

#### Custom Widget Pattern
```python
class CustomForm(forms.ModelForm):
    class Meta:
        model = MyModel
        fields = ['field1', 'field2']
        widgets = {
            'field1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter value'
            }),
        }
```

## 🎨 Frontend Development

### CSS Architecture

#### CSS Variables System
```css
:root {
  /* Colors */
  --primary-brown: #8B4513;
  --accent-cream: #F5F5DC;
  
  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  
  /* Animations */
  --transition-fast: 0.2s ease;
  --transition-smooth: 0.3s ease-in-out;
}
```

#### Component-Based CSS
```css
/* Card Component */
.card {
  background: var(--accent-cream);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(139, 69, 19, 0.1);
  transition: var(--transition-smooth);
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 48px rgba(139, 69, 19, 0.15);
}
```

#### Animation System
```css
/* Keyframe Animations */
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

### JavaScript Patterns

#### AJAX Request Pattern
```javascript
function updateCart(productId, quantity) {
    fetch('/orders/update-cart-item/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            updateCartDisplay(data);
        }
    });
}
```

#### Animation Trigger Pattern
```javascript
// Intersection Observer for scroll animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
        }
    });
}, observerOptions);
```

## 🗄️ Database Design

### Key Relationships

#### Product-Order Relationship
```
Product (1) ←→ (M) CartItem ←→ (1) Cart
Product (1) ←→ (M) OrderItem ←→ (1) Order
```

#### User-Profile Relationship
```
User (1) ←→ (1) UserProfile
User (1) ←→ (M) Order
User (1) ←→ (M) Review
```

#### Content Relationships
```
Category (1) ←→ (M) Product
Category (1) ←→ (M) Post
Post (M) ←→ (M) Tag
```

### Migration Best Practices

#### Creating Migrations
```bash
# Create migration for specific app
python manage.py makemigrations products

# Create empty migration for custom operations
python manage.py makemigrations --empty products

# Name migrations descriptively
python manage.py makemigrations products --name add_product_rating_field
```

#### Data Migrations
```python
from django.db import migrations

def populate_slugs(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    for product in Product.objects.all():
        if not product.slug:
            product.slug = slugify(product.name)
            product.save()

class Migration(migrations.Migration):
    operations = [
        migrations.RunPython(populate_slugs),
    ]
```

## 📧 Email System

### Email Template Structure
```
templates/
├── email/
│   ├── base_email.html          # Base email template
│   ├── verification_email.html   # Account verification
│   ├── password_reset.html       # Password reset
│   └── order_confirmation.html   # Order notifications
```

### Email Sending Pattern
```python
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_notification_email(user, template_name, context):
    subject = context.get('subject', 'Notification')
    html_message = render_to_string(f'email/{template_name}.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False
    )
```

## 🔍 Testing Strategy

### Unit Testing
```python
from django.test import TestCase
from django.contrib.auth.models import User
from products.models import Product

class ProductModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Product",
            price=100.00,
            tax_percentage=10.00
        )
    
    def test_price_with_tax(self):
        expected_price = 110.00
        self.assertEqual(self.product.get_price_with_tax(), expected_price)
```

### Integration Testing
```python
from django.test import Client, TestCase

class CartIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'password')
    
    def test_add_to_cart_flow(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post('/orders/add-to-cart/', {
            'product_id': self.product.id,
            'quantity': 2
        })
        self.assertEqual(response.status_code, 200)
```

## 🔧 Debugging

### Debug Settings
```python
# Development debugging
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']
```

### Logging Configuration
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Common Debug Commands
```bash
# Check for issues
python manage.py check

# Validate templates
python manage.py validate_templates

# Show SQL queries
python manage.py shell
>>> from django.db import connection
>>> connection.queries

# Debug email backend
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Message', 'from@test.com', ['to@test.com'])
```

## 🚀 Performance Optimization

### Database Optimization
```python
# Use select_related for foreign keys
products = Product.objects.select_related('category').all()

# Use prefetch_related for many-to-many
products = Product.objects.prefetch_related('media').all()

# Database indexing
class Product(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    sku = models.CharField(max_length=20, unique=True, db_index=True)
```

### Template Optimization
```html
<!-- Use template fragments for reusable components -->
{% include 'components/product_card.html' with product=product %}

<!-- Cache expensive template blocks -->
{% load cache %}
{% cache 3600 product_list category.id %}
    <!-- Expensive template content -->
{% endcache %}
```

### Static File Optimization
```python
# Compress static files in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Enable browser caching
WHITENOISE_MAX_AGE = 31536000  # 1 year
```

## 🔐 Security Best Practices

### Input Validation
```python
from django.core.validators import RegexValidator

class Product(models.Model):
    sku = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^[A-Z0-9-]+$', 'Invalid SKU format')]
    )
```

### CSRF Protection
```javascript
// Get CSRF token for AJAX requests
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
```

### File Upload Security
```python
def validate_image(image):
    file_size = image.file.size
    limit_mb = 5
    if file_size > limit_mb * 1024 * 1024:
        raise ValidationError(f"Max file size is {limit_mb}MB")
    
    # Validate file type
    if not image.name.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise ValidationError("Only PNG and JPEG files allowed")
```

## 📊 Custom Management Commands

### Creating Commands
```python
# orders/management/commands/send_abandoned_cart_emails.py
from django.core.management.base import BaseCommand
from orders.models import AbandonedCart

class Command(BaseCommand):
    help = 'Send abandoned cart reminder emails'
    
    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')
    
    def handle(self, *args, **options):
        abandoned_carts = AbandonedCart.objects.filter(
            email_sent=False,
            created_at__lte=timezone.now() - timedelta(hours=2)
        )
        
        for cart in abandoned_carts:
            if not options['dry_run']:
                cart.send_reminder_email()
            self.stdout.write(f"Processed cart: {cart.id}")
```

### Running Commands
```bash
# List all available commands
python manage.py help

# Run custom command
python manage.py send_abandoned_cart_emails

# Run with options
python manage.py send_abandoned_cart_emails --dry-run
```

## 🎯 API Development

### REST API Pattern
```python
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET', 'POST'])
def product_api(request):
    if request.method == 'GET':
        products = Product.objects.filter(is_active=True)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
```

### Serializer Pattern
```python
from rest_framework import serializers

class ProductSerializer(serializers.ModelSerializer):
    price_with_tax = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'price_with_tax', 'stock_quantity']
    
    def get_price_with_tax(self, obj):
        return obj.get_price_with_tax()
```

## 🔄 Background Tasks

### Celery Task Pattern
```python
# orders/tasks.py
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_abandoned_cart_email(cart_id):
    try:
        cart = AbandonedCart.objects.get(id=cart_id)
        cart.send_reminder_email()
        return f"Email sent for cart {cart_id}"
    except AbandonedCart.DoesNotExist:
        return f"Cart {cart_id} not found"
```

### Periodic Tasks
```python
# settings.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'send-abandoned-cart-emails': {
        'task': 'orders.tasks.send_abandoned_cart_emails',
        'schedule': crontab(minute=0),  # Every hour
    },
}
```

## 🧪 Testing Guidelines

### Test Structure
```
tests/
├── test_models.py      # Model unit tests
├── test_views.py       # View integration tests
├── test_forms.py       # Form validation tests
├── test_utils.py       # Utility function tests
└── test_api.py         # API endpoint tests
```

### Test Data Factories
```python
import factory
from django.contrib.auth.models import User

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product
    
    name = factory.Faker('word')
    price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
```

## 🔧 Utility Functions

### Common Utilities
```python
# core/utils.py
from django.utils.text import slugify
import random
import string

def generate_unique_slug(model_class, title):
    """Generate a unique slug for a model."""
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    
    while model_class.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    return slug

def generate_verification_code():
    """Generate a 6-digit verification code."""
    return ''.join(random.choices(string.digits, k=6))

def format_currency(amount):
    """Format currency with proper symbols."""
    return f"${amount:,.2f}"
```

## 📝 Code Style Guidelines

### Python Code Style
- Follow PEP 8 standards
- Use type hints where applicable
- Write descriptive docstrings
- Keep functions under 20 lines when possible
- Use meaningful variable names

### Template Guidelines
- Use semantic HTML5 elements
- Keep templates DRY with includes and extends
- Use template filters for data formatting
- Add comments for complex template logic

### CSS Guidelines
- Use CSS variables for consistency
- Follow BEM methodology for class naming
- Group related styles together
- Use mobile-first responsive design

## 🚀 Deployment Workflow

### Development to Production
1. **Code Review**: Peer review all changes
2. **Testing**: Run full test suite
3. **Migration Check**: Verify database migrations
4. **Static Files**: Update and collect static files
5. **Environment Config**: Update production settings
6. **Deploy**: Use automated deployment script
7. **Verify**: Test critical functionality
8. **Monitor**: Check logs and performance

### Rollback Procedure
```bash
# Database rollback
python manage_production.py migrate products 0001

# Code rollback
git checkout previous-stable-commit

# Restart services
sudo systemctl restart oraagh
sudo systemctl reload nginx
```

## 📚 Additional Resources

### Documentation Files
- `README.md`: Project overview and quick start
- `INSTALLATION.md`: Detailed setup instructions
- `deployment_guide.md`: Production deployment guide
- `setup_abandoned_cart_cron.md`: Abandoned cart setup
- `doc/overview.md`: Technical overview
- `doc/todo.md`: Development roadmap

### External Documentation
- [Django Documentation](https://docs.djangoproject.com/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Celery Documentation](https://docs.celeryproject.org/)

---

**Happy Coding! 🚀**
