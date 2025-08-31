from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Order
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Order)
def send_order_status_email(sender, instance, created, **kwargs):
    """
    Send email notification when order status changes
    """
    # Don't send email for newly created orders (already handled in views)
    if created:
        return
    
    # Check if status was actually changed
    if hasattr(instance, '_original_status'):
        if instance._original_status == instance.status:
            return  # Status didn't change, no email needed
    
    # Map status to email templates and subjects
    status_email_map = {
        'processing': {
            'template': 'orders/email/order_status_processing.html',
            'subject': 'Order Processing - Your Oraagh Order is Being Prepared'
        },
        'shipped': {
            'template': 'orders/email/order_status_shipped.html',
            'subject': 'Order Shipped - Your Oraagh Package is On Its Way'
        },
        'delivered': {
            'template': 'orders/email/order_status_delivered.html',
            'subject': 'Order Delivered - Your Oraagh Order Has Arrived'
        },
        'cancelled': {
            'template': 'orders/email/order_status_cancelled.html',
            'subject': 'Order Cancelled - Oraagh Order Cancellation Notice'
        }
    }
    
    # Get email configuration for current status
    email_config = status_email_map.get(instance.status)
    if not email_config:
        logger.warning(f"No email template configured for status: {instance.status}")
        return
    
    try:
        # Create mock request for template context
        class MockRequest:
            def __init__(self):
                self.scheme = 'https'
            
            def get_host(self):
                return getattr(settings, 'SITE_DOMAIN', 'oraagh.com')
        
        # Prepare email context
        context = {
            'order': instance,
            'user': instance.user,
            'request': MockRequest(),
        }
        
        # Add cancellation reason if status is cancelled
        if instance.status == 'cancelled':
            context['cancellation_reason'] = getattr(instance, 'cancellation_reason', 'Order cancelled as requested')
        
        # Render email templates
        html_message = render_to_string(email_config['template'], context)
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=email_config['subject'],
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.billing_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Order status email sent successfully to {instance.billing_email} for order {instance.order_number} (status: {instance.status})")
        
    except Exception as e:
        logger.error(f"Failed to send order status email for order {instance.order_number}: {str(e)}")
        # Don't raise the exception to avoid breaking the order save process


def track_order_status_changes():
    """
    Utility function to track status changes in Order model
    This should be called in the Order model's __init__ method
    """
    def __init__(self, *args, **kwargs):
        super(Order, self).__init__(*args, **kwargs)
        self._original_status = self.status
    
    return __init__
