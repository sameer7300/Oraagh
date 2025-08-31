# Abandoned Cart Email System Setup Guide

## Overview
The abandoned cart email system automatically sends reminder emails to users who:
1. Add items to cart but don't purchase within 2 hours
2. Start checkout process but don't complete within 1 hour

## Files Created
- `orders/models.py` - Added AbandonedCart model
- `orders/admin.py` - Added admin interface for abandoned carts
- `orders/views.py` - Added tracking functions
- `orders/templates/orders/email/abandoned_cart_reminder.html` - Cart reminder email
- `orders/templates/orders/email/abandoned_checkout_reminder.html` - Checkout reminder email
- `orders/management/commands/send_abandoned_cart_emails.py` - Management command
- `orders/tasks.py` - Celery task configuration

## Setup Instructions

### 1. Run Database Migration
```bash
python manage.py makemigrations orders
python manage.py migrate
```

### 2. Test the System
```bash
# Test email sending (dry run)
python manage.py send_abandoned_cart_emails --dry-run

# Send actual emails
python manage.py send_abandoned_cart_emails
```

### 3. Schedule Automated Emails

#### Option A: Windows Task Scheduler
1. Create a batch file `send_abandoned_cart_emails.bat`:
```batch
@echo off
cd "C:\Users\samee\OneDrive\Desktop\unique and antique\RED sun MINING"
python manage.py send_abandoned_cart_emails
```

2. Open Task Scheduler and create a new task:
   - Trigger: Every hour
   - Action: Start the batch file

#### Option B: Celery (Recommended for production)
1. Install Celery: `pip install celery redis`
2. Add to settings.py:
```python
# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_BEAT_SCHEDULE = {
    'send-abandoned-cart-emails': {
        'task': 'orders.tasks.send_abandoned_cart_emails',
        'schedule': 3600.0,  # Run every hour
    },
}
```

3. Run Celery worker and beat:
```bash
celery -A redsunmining worker --loglevel=info
celery -A redsunmining beat --loglevel=info
```

## Email Templates
- **Cart Reminder**: Sent after 2 hours of cart inactivity
- **Checkout Reminder**: Sent after 1 hour of checkout abandonment
- Both templates use Oraagh branding with brown/gold color scheme

## Admin Interface
Access abandoned cart records at: `/admin/orders/abandonedcart/`
- View all abandoned carts
- Track email sending status
- Monitor recovery rates

## Configuration
Edit timing in `orders/models.py`:
- Cart reminder: `get_hours_since_last_activity() >= 2`
- Checkout reminder: `(timezone.now() - self.checkout_started_at).total_seconds() / 3600 >= 1`

## Monitoring
- Check admin interface for abandoned cart statistics
- Monitor email logs for delivery status
- Track recovery rates to optimize timing
