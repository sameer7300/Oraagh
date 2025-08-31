# Production Deployment Guide - Red Sun Mining (Oraagh)

Complete guide for deploying the Red Sun Mining e-commerce platform to production environments.

## 🎯 Deployment Overview

### Supported Platforms
- **VPS/Dedicated Servers**: Ubuntu 20.04+, CentOS 8+
- **Cloud Platforms**: AWS EC2, Google Cloud, DigitalOcean
- **Web Hosting**: cPanel, Shared hosting with Python support

### Architecture Components
```
Load Balancer (Nginx) → Web Server (Gunicorn) → Database (MySQL)
                     ↓                        ↓
                Static Files              Redis Cache
```

## 🚀 Quick Production Deployment

### Automated Setup
```bash
# 1. Clone repository
git clone <repository-url> /var/www/oraagh
cd /var/www/oraagh

# 2. Run automated setup
python setup_production.py

# 3. Configure web server
```

## 🗄️ Database Setup

### MySQL Configuration
```sql
CREATE DATABASE oraagh_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'oraagh_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON oraagh_db.* TO 'oraagh_user'@'localhost';
FLUSH PRIVILEGES;
```

### Backup Strategy
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u oraagh_user -p oraagh_db > /var/backups/oraagh_$DATE.sql
gzip /var/backups/oraagh_$DATE.sql
```

## 🌐 Web Server Configuration

### Nginx Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name oraagh.com www.oraagh.com;
    
    ssl_certificate /etc/ssl/certs/oraagh.com.crt;
    ssl_certificate_key /etc/ssl/private/oraagh.com.key;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /var/www/oraagh/staticfiles/;
        expires 1y;
    }
    
    location /media/ {
        alias /var/www/oraagh/media/;
        expires 30d;
    }
}
```

### Gunicorn Service
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

## 🔒 Security Configuration

### Environment Variables
```env
SECRET_KEY=your-very-long-random-secret-key
DEBUG=False
ALLOWED_HOSTS=oraagh.com,www.oraagh.com
DB_NAME=oraagh_db
DB_USER=oraagh_user
DB_PASSWORD=secure_password
EMAIL_HOST_USER=info@oraagh.com
EMAIL_HOST_PASSWORD=app_password
```

### SSL Setup
```bash
# Let's Encrypt
sudo certbot --nginx -d oraagh.com -d www.oraagh.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring & Logging

### Log Configuration
```python
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/www/oraagh/logs/django.log',
            'maxBytes': 15728640,  # 15MB
            'backupCount': 10,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

### Health Check
```python
def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({'status': 'healthy'})
    except Exception as e:
        return JsonResponse({'status': 'unhealthy', 'error': str(e)}, status=503)
```

## 🔄 Automated Tasks

### Celery Configuration
```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_BEAT_SCHEDULE = {
    'send-abandoned-cart-emails': {
        'task': 'orders.tasks.send_abandoned_cart_emails',
        'schedule': 3600.0,  # Every hour
    },
}
```

### Cron Jobs
```bash
# Edit crontab
crontab -e

# Add abandoned cart emails
0 * * * * cd /var/www/oraagh && /var/www/oraagh/venv/bin/python manage_production.py send_abandoned_cart_emails

# Daily backup
0 2 * * * /var/www/oraagh/scripts/backup.sh

# Log cleanup
0 3 * * 0 find /var/www/oraagh/logs -name "*.log" -mtime +30 -delete
```

## 🔍 Troubleshooting

### Common Issues

#### 502 Bad Gateway
```bash
sudo systemctl status oraagh
sudo journalctl -u oraagh -f
sudo systemctl restart oraagh nginx
```

#### Database Connection
```bash
mysql -u oraagh_user -p oraagh_db
sudo systemctl status mysql
```

#### Static Files
```bash
python manage_production.py collectstatic --clear --noinput
sudo chown -R www-data:www-data staticfiles/
```

### Performance Monitoring
```bash
# System resources
htop
df -h
free -h

# Database performance
mysql -u root -p -e "SHOW PROCESSLIST;"

# Application logs
tail -f /var/www/oraagh/logs/django.log
```

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Code reviewed and tested
- [ ] Environment variables configured
- [ ] Database backup created
- [ ] SSL certificate ready
- [ ] DNS records configured

### Deployment Steps
- [ ] Pull latest code
- [ ] Install/update dependencies
- [ ] Run database migrations
- [ ] Collect static files
- [ ] Restart application server
- [ ] Test critical functionality

### Post-Deployment
- [ ] Verify site accessibility
- [ ] Test user registration/login
- [ ] Test cart and checkout
- [ ] Test email functionality
- [ ] Monitor error logs
- [ ] Update monitoring systems

## 🚨 Emergency Procedures

### Site Down Response
1. Check service status
2. Review error logs
3. Restart services
4. Test database connection
5. Notify stakeholders

### Rollback Process
```bash
git checkout <previous-stable-commit>
python manage_production.py migrate <app> <previous_migration>
sudo systemctl restart oraagh
```

---

**For detailed server-specific instructions, refer to the existing `deployment_guide.md` file.**
