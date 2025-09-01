# Oraagh - Premium Woolen Products E-commerce Platform

![Oraagh Logo](staticfiles/oraagh1.png)

A premium Django-based e-commerce platform specializing in luxury woolen products and textiles. Built with modern web technologies and featuring a sophisticated brown/cream luxury theme.

## 🌟 Features

### Core E-commerce Features
- **Product Management**: Comprehensive product catalog with categories, SKUs, pricing, and inventory
- **Shopping Cart**: Advanced cart functionality with quantity management and abandoned cart recovery
- **Order Processing**: Complete order lifecycle with status tracking and notifications
- **User Authentication**: Secure registration/login with email verification using 6-digit codes
- **Review System**: Customer reviews with admin moderation and email notifications
- **Deal Requests**: Customer inquiry system for special requests and negotiations

### Advanced Features
- **Admin Dashboard**: Custom admin interface with statistics, order management, and content control
- **Newsletter System**: Email marketing with subscriber management and campaign sending
- **Blog Platform**: Content management system with categories, tags, and SEO optimization
- **Abandoned Cart Recovery**: Automated email reminders for incomplete purchases
- **Multi-level Navigation**: Breadcrumb navigation and category filtering

### Frontend Excellence
- **Luxury Design**: Premium brown/cream/beige color scheme with glassmorphism effects
- **Advanced Animations**: Shimmer effects, 3D transforms, parallax scrolling, and micro-interactions
- **Responsive Design**: Mobile-first approach with optimized layouts for all devices
- **Interactive Components**: Image galleries, product sliders, and dynamic form validation
- **Performance Optimized**: Lazy loading, CSS animations, and optimized asset delivery

## 🏗️ Architecture

### Django Apps Structure
```
├── core/           # Home page, navigation, and base functionality
├── accounts/       # User authentication and profile management
├── products/       # Product catalog, reviews, and deal requests
├── orders/         # Shopping cart, checkout, and order management
├── blog/           # Content management and blog functionality
├── contact/        # Contact forms and communication
├── newsletter/     # Email marketing and subscriber management
└── admin_dashboard/# Custom admin interface and management tools
```

### Technology Stack
- **Backend**: Django 4.2.7, Python 3.x
- **Database**: MySQL (Production), SQLite (Development)
- **Frontend**: HTML5, CSS3, JavaScript, Tailwind CSS
- **Email**: SMTP with HTML templates
- **File Storage**: Local storage with media management
- **Security**: HTTPS, CSRF protection, rate limiting
- **Deployment**: Gunicorn, WhiteNoise, Apache/Nginx

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MySQL (for production)
- Node.js (for frontend assets)
- Git

### Development Setup
```bash
# Clone the repository
git clone <repository-url>
cd "RED sun MINING"

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run development server
python manage.py runserver
```

### Production Deployment
```bash
# Use production requirements
pip install -r requirements_production.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your production values

# Run production setup
python setup_production.py

# Start with production settings
python manage_production.py runserver
```

## 📁 Project Structure

```
RED sun MINING/
├── accounts/                 # User management
│   ├── models.py            # User profiles, verification codes
│   ├── views.py             # Authentication views
│   ├── forms.py             # User forms
│   └── templates/           # Auth templates
├── admin_dashboard/         # Admin interface
│   ├── views.py             # Dashboard views
│   ├── forms.py             # Admin forms
│   └── templates/           # Admin templates
├── blog/                    # Content management
│   ├── models.py            # Post, Category, Tag models
│   ├── views.py             # Blog views
│   └── templates/           # Blog templates
├── contact/                 # Contact functionality
│   ├── views.py             # Contact form handling
│   ├── forms.py             # Contact forms
│   └── templates/           # Contact templates
├── core/                    # Base functionality
│   ├── models.py            # Core models
│   ├── views.py             # Home, about pages
│   ├── templates/           # Base templates
│   └── static/              # Core CSS/JS
├── newsletter/              # Email marketing
│   ├── models.py            # Subscriber model
│   ├── views.py             # Newsletter views
│   └── templates/           # Email templates
├── orders/                  # E-commerce core
│   ├── models.py            # Cart, Order, AbandonedCart
│   ├── views.py             # Cart and checkout
│   ├── management/          # Cart reminder commands
│   └── templates/           # Order templates
├── products/                # Product catalog
│   ├── models.py            # Product, Review, DealRequest
│   ├── views.py             # Product listing and details
│   ├── forms.py             # Product forms
│   └── templates/           # Product templates
├── redsunmining/           # Django settings
│   ├── settings.py          # Development settings
│   ├── urls.py              # URL configuration
│   └── wsgi.py              # WSGI configuration
├── staticfiles/             # Collected static files
├── doc/                     # Documentation
├── production_settings.py   # Production configuration
├── manage_production.py     # Production management
├── requirements.txt         # Development dependencies
├── requirements_production.txt # Production dependencies
└── deployment_guide.md      # Deployment instructions
```

## 🎨 Design System

### Color Palette
```css
:root {
  --primary-brown: #8B4513;      /* Main brand color */
  --primary-brown-dark: #654321;  /* Dark variant */
  --neutral-brown-light: #A0522D; /* Light variant */
  --accent-cream: #F5F5DC;        /* Background/accent */
  --cream-100: #FEFEFE;           /* Light background */
  --warm-beige: #F4E4BC;          /* Warm accent */
}
```

### Typography
- **Headings**: Playfair Display (serif, elegant)
- **Body Text**: Inter (sans-serif, modern)
- **Accent**: Cormorant Garamond (serif, classic)

### UI Components
- **Glassmorphism Cards**: Translucent backgrounds with blur effects
- **3D Transforms**: Hover animations with perspective
- **Gradient Buttons**: Multi-stop gradients with shimmer effects
- **Interactive Forms**: Floating labels and validation feedback

## 🔧 Configuration

### Environment Variables
Create a `.env` file based on `.env.example`:
```env
SECRET_KEY=your-secret-key-here
DB_NAME=oraagh_db
DB_USER=oraagh_user
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=3306
EMAIL_HOST_USER=info@oraagh.com
EMAIL_HOST_PASSWORD=your-email-password
DEBUG=False
ALLOWED_HOSTS=oraagh.com,www.oraagh.com
```

### Database Configuration
```sql
CREATE DATABASE oraagh_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'oraagh_user'@'localhost' IDENTIFIED BY 'your-password';
GRANT ALL PRIVILEGES ON oraagh_db.* TO 'oraagh_user'@'localhost';
```

## 📧 Email System

### Email Features
- **User Verification**: 6-digit codes for email verification
- **Password Reset**: Secure password reset with expiring codes
- **Order Notifications**: Automated order confirmations
- **Review Notifications**: Admin alerts for new reviews
- **Abandoned Cart**: Automated recovery emails
- **Newsletter**: Marketing campaigns and updates

### Email Templates
- HTML templates with fallback text versions
- Consistent branding with luxury styling
- Responsive design for mobile devices
- Personalized content with user data

## 🛡️ Security Features

### Authentication & Authorization
- **Django Authentication**: Built-in user system with custom profiles
- **Email Verification**: Required for account activation
- **Password Security**: Strong password requirements
- **Rate Limiting**: Protection against brute force attacks
- **CSRF Protection**: Cross-site request forgery prevention

### Production Security
- **HTTPS Enforcement**: SSL/TLS configuration
- **Security Headers**: XSS protection, content type sniffing prevention
- **Database Security**: Parameterized queries, connection encryption
- **File Upload Security**: Validated file types and sizes

## 🔄 Business Logic

### Product Management
- **Inventory Tracking**: Real-time stock management
- **Pricing System**: Base price + tax calculations
- **Category Organization**: Hierarchical product categorization
- **Media Management**: Multiple images per product
- **SEO Optimization**: Slug-based URLs and meta tags

### Order Processing
1. **Cart Management**: Add/remove/update items
2. **Checkout Process**: Customer information collection
3. **Order Creation**: Generate order with unique ID
4. **Status Tracking**: Order lifecycle management
5. **Email Notifications**: Automated customer updates

### Customer Experience
- **Product Discovery**: Search, filter, and sort functionality
- **Detailed Views**: Comprehensive product information
- **Review System**: Customer feedback and ratings
- **Inquiry System**: Direct communication for special requests
- **Account Management**: Order history and profile updates

## 📊 Admin Features

### Dashboard Overview
- **Statistics**: Products, orders, customers, and blog metrics
- **Quick Actions**: Fast access to common tasks
- **Recent Activity**: Latest products and orders
- **System Information**: Status and health monitoring

### Management Tools
- **Product CRUD**: Create, read, update, delete products
- **Order Management**: View, update, and track orders
- **Customer Management**: User accounts and profiles
- **Content Management**: Blog posts and categories
- **Review Moderation**: Approve/reject customer reviews
- **Newsletter Campaigns**: Create and send marketing emails

## 🔧 Development

### Code Quality
- **PEP 8 Compliance**: Python code style standards
- **Type Hints**: Enhanced code documentation
- **Error Handling**: Comprehensive exception management
- **Logging**: Detailed application logging
- **Testing**: Unit tests for critical functionality

### Performance Optimization
- **Database Indexing**: Optimized query performance
- **Static File Compression**: Minified CSS/JS
- **Image Optimization**: Compressed media files
- **Caching Strategy**: Redis-based caching
- **CDN Integration**: Static file delivery optimization

## 📱 Mobile Experience

### Responsive Design
- **Mobile-First**: Optimized for mobile devices
- **Touch Interactions**: Gesture-friendly interface
- **Performance**: Fast loading on mobile networks
- **Accessibility**: Screen reader compatible
- **Progressive Enhancement**: Works without JavaScript

## 🚀 Deployment

### Production Environment
- **Server**: Apache/Nginx with WSGI
- **Database**: MySQL with connection pooling
- **Static Files**: WhiteNoise for static file serving
- **Email**: SMTP with authentication
- **SSL**: HTTPS with security headers
- **Monitoring**: Application and server monitoring

### Automated Deployment
```bash
# Run the automated setup script
python setup_production.py
```

## 📈 Analytics & Monitoring

### Built-in Analytics
- **Product Views**: Track popular products
- **Order Analytics**: Sales performance metrics
- **User Engagement**: Registration and activity tracking
- **Cart Analytics**: Abandonment and recovery rates

### Monitoring Tools
- **Django Logging**: Application-level logging
- **Error Tracking**: Exception monitoring
- **Performance Metrics**: Response time tracking
- **Health Checks**: System status monitoring

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

### Code Standards
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for functions and classes
- Write unit tests for new features
- Update documentation for changes

## 📞 Support

### Getting Help
- **Documentation**: Check the `doc/` directory
- **Issues**: Create GitHub issues for bugs
- **Email**: Contact info@oraagh.com
- **Community**: Join our developer community

### Common Issues
- **Database Connection**: Check `.env` configuration
- **Static Files**: Run `collectstatic` command
- **Email Setup**: Verify SMTP settings
- **Permissions**: Check file and directory permissions

## 📄 License

This project is proprietary software. All rights reserved.

## 🏆 Acknowledgments

- **Django Community**: For the excellent web framework
- **Bootstrap/Tailwind**: For responsive design components
- **Font Awesome**: For beautiful icons
- **Google Fonts**: For premium typography

---

**Built with ❤️ for premium woolen products**

*Last updated: August 31, 2025*
