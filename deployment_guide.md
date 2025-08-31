# Oraagh.com Deployment Guide for HosterPK

## 📋 Pre-Deployment Checklist

### 1. Files Created for Production
- ✅ `production_settings.py` - Production Django settings
- ✅ `requirements_production.txt` - Essential production packages
- ✅ `.env.example` - Environment variables template
- ✅ `wsgi.py` - Production WSGI configuration
- ✅ `manage_production.py` - Production management script

### 2. Environment Setup

#### Create `.env` file on server:
```bash
# Copy the example and fill in real values
cp .env.example .env
```

#### Required environment variables:
```env
SECRET_KEY=your-super-secret-key-here
DB_NAME=oraagh_db
DB_USER=oraagh_user
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=3306
EMAIL_HOST_USER=info@oraagh.com
EMAIL_HOST_PASSWORD=your-email-password
DEBUG=False
```

### 3. Database Setup

#### MySQL Database Configuration:
```sql
CREATE DATABASE oraagh_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'oraagh_user'@'localhost' IDENTIFIED BY 'your-password';
GRANT ALL PRIVILEGES ON oraagh_db.* TO 'oraagh_user'@'localhost';
FLUSH PRIVILEGES;
```

## 🚀 Deployment Steps

### 1. Upload Files to Server
Upload all project files to your application root directory: `/home1/oraaghco/oraagh`

### 2. Install Dependencies
```bash
pip install -r requirements_production.txt
```

### 3. Configure Database
```bash
python manage_production.py makemigrations
python manage_production.py migrate
```

### 4. Create Superuser
```bash
python manage_production.py createsuperuser
```

### 5. Collect Static Files
```bash
python manage_production.py collectstatic --noinput
```

### 6. Create Required Directories
```bash
mkdir -p logs
mkdir -p cache
mkdir -p media
chmod 755 media
chmod 755 staticfiles
```

## ⚙️ Server Configuration

### Apache Configuration (.htaccess)
Create `.htaccess` in your domain root:
```apache
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ wsgi.py/$1 [QSA,L]

# Static files
Alias /static/ /home1/oraaghco/public_html/oraagh/staticfiles/
Alias /media/ /home1/oraaghco/public_html/oraagh/media/

<Directory "/home1/oraaghco/public_html/oraagh/staticfiles">
    Require all granted
</Directory>

<Directory "/home1/oraaghco/public_html/oraagh/media">
    Require all granted
</Directory>
```

### Nginx Configuration (if using Nginx)
```nginx
server {
    listen 80;
    server_name oraagh.com www.oraagh.com;
    
    location /static/ {
        alias /home1/oraaghco/public_html/oraagh/staticfiles/;
    }
    
    location /media/ {
        alias /home1/oraaghco/public_html/oraagh/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔒 Security Checklist

### SSL Certificate
- [ ] Install SSL certificate for oraagh.com
- [ ] Enable HTTPS redirect
- [ ] Update production_settings.py to enable SSL settings

### File Permissions
```bash
chmod 644 *.py
chmod 755 manage_production.py
chmod 600 .env
```

### Security Headers
Ensure these are enabled in `production_settings.py`:
- ✅ SECURE_BROWSER_XSS_FILTER
- ✅ SECURE_CONTENT_TYPE_NOSNIFF
- ✅ SECURE_HSTS_SECONDS
- ✅ X_FRAME_OPTIONS

## 📧 Email Configuration

### Email Settings Verification
Test email functionality:
```bash
python manage_production.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'info@oraagh.com', ['test@example.com'])
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Static Files Not Loading
```bash
python manage_production.py collectstatic --clear --noinput
```

#### 2. Database Connection Issues
- Verify database credentials in `.env`
- Check MySQL service is running
- Ensure user has proper permissions

#### 3. Email Not Working
- Verify email credentials
- Check firewall settings for SMTP ports
- Test with hosting provider's SMTP settings

#### 4. Permission Errors
```bash
chown -R www-data:www-data /path/to/project
chmod -R 755 /path/to/project
```

## 📊 Monitoring

### Log Files
- Django logs: `logs/django.log`
- Server logs: Check hosting control panel

### Health Checks
- Admin panel: `https://oraagh.com/admin/`
- API status: `https://oraagh.com/api/`
- Email functionality: Test order confirmations

## 🎯 Post-Deployment Tasks

### 1. Test Core Functionality
- [ ] User registration/login
- [ ] Product browsing
- [ ] Cart functionality
- [ ] Order placement
- [ ] Email notifications
- [ ] Admin panel access

### 2. Performance Optimization
- [ ] Enable caching
- [ ] Optimize database queries
- [ ] Configure CDN for static files
- [ ] Set up monitoring

### 3. Backup Strategy
- [ ] Database backups
- [ ] Media files backup
- [ ] Code repository backup

## 📞 Support Contacts

- **Hosting Provider**: HosterPK Support
- **Domain**: oraagh.com
- **Email**: info@oraagh.com

---

**Note**: Always test in a staging environment before deploying to production!
