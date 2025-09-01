# Contributing to (Oraagh)

Thank you for your interest in contributing to the Oraagh woolen e-commerce platform! This guide outlines how to contribute effectively.

## 🤝 How to Contribute

### Types of Contributions
- **Bug Reports**: Help us identify and fix issues
- **Feature Requests**: Suggest new functionality
- **Code Contributions**: Submit improvements and new features
- **Documentation**: Improve guides and documentation
- **Testing**: Help test new features and bug fixes

## 🐛 Reporting Bugs

### Before Reporting
- Check existing issues to avoid duplicates
- Test on the latest version
- Gather relevant information (browser, OS, steps to reproduce)

### Bug Report Template
```markdown
**Bug Description**
A clear description of the bug.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment**
- OS: [e.g., Windows 10]
- Browser: [e.g., Chrome 91]
- Version: [e.g., v1.2.0]
```

## 💡 Feature Requests

### Feature Request Template
```markdown
**Feature Description**
Clear description of the proposed feature.

**Problem Statement**
What problem does this solve?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
Other solutions you've considered.

**Additional Context**
Any other relevant information.
```

## 🔧 Development Setup

### Prerequisites
- Python 3.8+
- Git
- MySQL (for production testing)
- Node.js (for frontend assets)

### Setup Steps
```bash
# Fork and clone
git clone https://github.com/yourusername/oraagh.git
cd red-sun-mining

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate

# Run tests
python manage.py test

# Start development server
python manage.py runserver
```

## 📝 Code Standards

### Python Code Style
- Follow PEP 8 guidelines
- Use type hints where applicable
- Write descriptive docstrings
- Maximum line length: 88 characters
- Use meaningful variable names

### Example Code Style
```python
from typing import Optional, List
from django.db import models

class Product(models.Model):
    """Model representing a woolen product."""
    
    name: str = models.CharField(max_length=255, help_text="Product name")
    price: Decimal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def get_price_with_tax(self) -> Decimal:
        """Calculate price including tax percentage."""
        tax_amount = self.price * (self.tax_percentage / 100)
        return self.price + tax_amount
```

### Frontend Code Style
- Use semantic HTML5 elements
- Follow CSS BEM methodology
- Use CSS variables for consistency
- Write accessible code (ARIA labels, alt text)
- Mobile-first responsive design

### Template Guidelines
```html
<!-- Use semantic HTML -->
<article class="product-card">
    <header class="product-card__header">
        <h2 class="product-card__title">{{ product.name }}</h2>
    </header>
    <div class="product-card__content">
        <!-- Content -->
    </div>
</article>

<!-- Use template filters -->
{{ product.price|floatformat:2 }}
{{ product.created_at|date:"M d, Y" }}
```

## 🧪 Testing Guidelines

### Writing Tests
```python
from django.test import TestCase, Client
from django.contrib.auth.models import User
from products.models import Product

class ProductViewTest(TestCase):
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.product = Product.objects.create(
            name='Test Product',
            price=100.00,
            stock_quantity=10
        )
    
    def test_product_detail_view(self):
        """Test product detail page loads correctly."""
        response = self.client.get(f'/products/{self.product.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
```

### Test Coverage
- Aim for 80%+ test coverage
- Test critical business logic
- Test edge cases and error conditions
- Include integration tests for workflows

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test products

# Run with coverage
coverage run manage.py test
coverage report
coverage html
```

## 🔄 Git Workflow

### Branch Naming
- **Features**: `feature/add-product-reviews`
- **Bug Fixes**: `bugfix/fix-cart-calculation`
- **Hotfixes**: `hotfix/security-patch`
- **Documentation**: `docs/update-readme`

### Commit Messages
```
feat: add product review system

- Add Review model with rating and comment fields
- Create review submission form and view
- Add review display to product detail page
- Include email notifications for new reviews

Closes #123
```

### Pull Request Process
1. **Create Branch**: From latest main branch
2. **Make Changes**: Follow code standards
3. **Write Tests**: Ensure good test coverage
4. **Update Docs**: Update relevant documentation
5. **Submit PR**: Use the PR template

### Pull Request Template
```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No console errors
```

## 🔍 Code Review Guidelines

### Review Checklist
- **Functionality**: Does the code work as intended?
- **Code Quality**: Is it readable and maintainable?
- **Performance**: Are there any performance issues?
- **Security**: Are there security vulnerabilities?
- **Tests**: Are tests comprehensive and passing?
- **Documentation**: Is documentation updated?

### Review Comments
- Be constructive and specific
- Suggest improvements, don't just point out problems
- Ask questions to understand the approach
- Approve when ready, request changes when needed

## 🚀 Release Process

### Version Numbering
- **Major**: Breaking changes (1.0.0 → 2.0.0)
- **Minor**: New features (1.0.0 → 1.1.0)
- **Patch**: Bug fixes (1.0.0 → 1.0.1)

### Release Checklist
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Migration files created
- [ ] Security review completed
- [ ] Performance testing done
- [ ] Staging deployment tested
- [ ] Release notes written

## 🏗️ Project Structure

### Adding New Apps
```bash
# Create new Django app
python manage.py startapp newapp

# Add to INSTALLED_APPS in settings.py
INSTALLED_APPS = [
    # ...
    'newapp',
]

# Create URL configuration
# newapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='newapp_index'),
]

# Include in main URLs
# redsunmining/urls.py
urlpatterns = [
    # ...
    path('newapp/', include('newapp.urls')),
]
```

### File Organization
```
newapp/
├── migrations/          # Database migrations
├── templates/newapp/    # App-specific templates
├── static/newapp/       # App-specific static files
├── management/          # Custom management commands
│   └── commands/
├── tests/              # Test files
├── __init__.py
├── admin.py            # Admin configuration
├── apps.py             # App configuration
├── forms.py            # Form definitions
├── models.py           # Data models
├── urls.py             # URL patterns
├── views.py            # View functions/classes
└── utils.py            # Utility functions
```

## 🔧 Development Tools

### Useful Commands
```bash
# Database operations
python manage.py makemigrations
python manage.py migrate
python manage.py dbshell

# Static files
python manage.py collectstatic
python manage.py findstatic filename.css

# User management
python manage.py createsuperuser
python manage.py changepassword username

# Development
python manage.py shell
python manage.py runserver 0.0.0.0:8000
```

### IDE Configuration
- **VS Code**: Install Python and Django extensions
- **PyCharm**: Configure Django project settings
- **Vim**: Use django.vim plugin
- **Sublime**: Install Django packages

### Debugging Tools
```python
# Use Django debug toolbar
if DEBUG:
    import debug_toolbar
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

# Use pdb for debugging
import pdb; pdb.set_trace()

# Use logging for production debugging
import logging
logger = logging.getLogger(__name__)
logger.info("Debug message")
```

## 📚 Learning Resources

### Django Resources
- [Django Documentation](https://docs.djangoproject.com/)
- [Django Best Practices](https://django-best-practices.readthedocs.io/)
- [Two Scoops of Django](https://www.feldroy.com/books/two-scoops-of-django-3-x)

### Frontend Resources
- [MDN Web Docs](https://developer.mozilla.org/)
- [CSS Tricks](https://css-tricks.com/)
- [JavaScript.info](https://javascript.info/)

### Testing Resources
- [Django Testing Documentation](https://docs.djangoproject.com/en/4.2/topics/testing/)
- [Python Testing 101](https://realpython.com/python-testing/)

## 🎯 Getting Started Checklist

- [ ] Read this contributing guide
- [ ] Set up development environment
- [ ] Run the test suite
- [ ] Make a small test change
- [ ] Submit your first pull request
- [ ] Join the developer community

## 📞 Community

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **Email**: dev@oraagh.com for development questions
- **Code Reviews**: All pull requests reviewed by maintainers

### Code of Conduct
- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow project guidelines

---

**Thank you for contributing to Red Sun Mining! Your help makes this project better for everyone. 🚀**
