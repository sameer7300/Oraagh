# Installation Guide - Oraagh Premium Woolen Products

This guide provides step-by-step instructions for setting up the Oraagh premium woolen products e-commerce platform in both development and production environments.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Database**: MySQL 8.0+ (production) or SQLite (development)
- **Memory**: Minimum 2GB RAM
- **Storage**: 5GB free space
- **OS**: Windows, macOS, or Linux

### Required Software
- **Git**: For version control
- **Python**: With pip package manager
- **MySQL**: Database server (production only)
- **Redis**: For caching and Celery (optional)

## 🛠️ Development Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd "RED sun MINING"
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
# For development, you can use default SQLite settings
```

### 5. Database Setup
```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser account
python manage.py createsuperuser
```

### 6. Static Files
```bash
# Collect static files
python manage.py collectstatic --noinput
```

### 7. Load Sample Data (Optional)
```bash
# Load initial data if available
python manage.py loaddata fixtures/sample_data.json
```

### 8. Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to see your application.

## 🏭 Production Setup

### 1. Server Preparation
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3 python3-pip python3-venv mysql-server nginx git
```

### 2. MySQL Database Setup
```sql
# Connect to MySQL
mysql -u root -p

# Create database and user
CREATE DATABASE oraagh_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'oraagh_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON oraagh_db.* TO 'oraagh_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Application Setup
```bash
# Clone repository to production directory
cd /var/www
sudo git clone <repository-url> oraagh
cd oraagh

# Create virtual environment
sudo python3 -m venv venv
sudo chown -R www-data:www-data venv
source venv/bin/activate

# Install production dependencies
pip install -r requirements_production.txt
```

### 4. Environment Configuration
```bash
# Create production environment file
sudo cp .env.example .env
sudo nano .env
```

Configure the following variables:
```env
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=oraagh_db
DB_USER=oraagh_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=3306

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Admin
ADMIN_EMAIL=admin@yourdomain.com
```

### 5. Automated Production Setup
```bash
# Run the automated setup script
sudo python setup_production.py
```

This script will:
- Install dependencies
- Run database migrations
- Collect static files
- Create superuser account
- Set up logging directories

### 6. Web Server Configuration

#### Nginx Configuration
Create `/etc/nginx/sites-available/oraagh`:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/private.key;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/oraagh/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/oraagh/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
}
```

#### Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/oraagh /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 7. Gunicorn Service
Create `/etc/systemd/system/oraagh.service`:
```ini
[Unit]
Description=Oraagh Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/oraagh
Environment="PATH=/var/www/oraagh/venv/bin"
ExecStart=/var/www/oraagh/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 redsunmining.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable oraagh
sudo systemctl start oraagh
```

## 🔄 Abandoned Cart Setup

### 1. Create Cron Job
```bash
# Edit crontab
crontab -e

# Add this line to run every hour
0 * * * * cd /var/www/oraagh && /var/www/oraagh/venv/bin/python manage_production.py send_abandoned_cart_emails
```

### 2. Alternative: Celery Setup
```bash
# Install Redis
sudo apt install redis-server

# Install Celery
pip install celery redis

# Start Celery worker
celery -A redsunmining worker --loglevel=info

# Start Celery beat (in separate terminal)
celery -A redsunmining beat --loglevel=info
```

## 🧪 Testing Installation

### 1. Test Database Connection
```bash
python manage_production.py shell
>>> from django.db import connection
>>> connection.ensure_connection()
>>> print("Database connection successful!")
```

### 2. Test Email Configuration
```bash
python test_email.py
```

### 3. Test Static Files
```bash
# Check if static files are served correctly
curl http://yourdomain.com/static/core/css/theme.css
```

### 4. Test Application
- Visit your domain
- Create a test account
- Add products to cart
- Test checkout process
- Verify email notifications

## 🔍 Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check MySQL service
sudo systemctl status mysql

# Test connection
mysql -u oraagh_user -p oraagh_db
```

#### Static Files Not Loading
```bash
# Recollect static files
python manage_production.py collectstatic --clear --noinput

# Check permissions
sudo chown -R www-data:www-data staticfiles/
```

#### Email Not Sending
```bash
# Test email configuration
python test_email.py

# Check email logs
tail -f logs/django.log | grep email
```

#### Permission Errors
```bash
# Fix ownership
sudo chown -R www-data:www-data /var/www/oraagh

# Fix permissions
sudo chmod -R 755 /var/www/oraagh
sudo chmod -R 644 /var/www/oraagh/staticfiles
```

### Log Files
- **Application Logs**: `logs/django.log`
- **Error Logs**: `logs/error.log`
- **Nginx Logs**: `/var/log/nginx/access.log`
- **System Logs**: `/var/log/syslog`

## 🔧 Development Tools

### Useful Commands
```bash
# Database shell
python manage.py dbshell

# Django shell
python manage.py shell

# Create migrations
python manage.py makemigrations

# Show migrations
python manage.py showmigrations

# Reset migrations (development only)
python manage.py migrate <app_name> zero
```

### Development Server Options
```bash
# Run on specific port
python manage.py runserver 8080

# Run on all interfaces
python manage.py runserver 0.0.0.0:8000

# Run with production settings
python manage_production.py runserver
```

## 📊 Performance Optimization

### Database Optimization
```python
# Add to settings.py for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
        'CONN_MAX_AGE': 3600,  # Connection pooling
    }
}
```

### Caching Setup
```python
# Redis caching configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

## 🔐 Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Set DEBUG=False in production
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable HTTPS/SSL
- [ ] Set up security headers
- [ ] Configure database user permissions
- [ ] Set up regular backups
- [ ] Enable logging and monitoring
- [ ] Test email functionality
- [ ] Verify file upload restrictions

---

For additional help, refer to the `deployment_guide.md` or contact the development team.
