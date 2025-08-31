#!/usr/bin/env python
"""
Test script for order status change emails
Run this script to test the order status email system
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'redsunmining.settings')
django.setup()

from orders.models import Order
from django.contrib.auth.models import User
from django.core.mail import send_mail


def test_order_status_emails():
    """Test order status change emails"""
    
    print("🧪 Testing Order Status Change Email System")
    print("=" * 50)
    
    # Find an existing order or create a test scenario
    try:
        # Get the first order for testing
        order = Order.objects.first()
        if not order:
            print("❌ No orders found in database. Please create an order first.")
            return
        
        print(f"📦 Testing with Order: {order.order_number}")
        print(f"👤 Customer: {order.billing_name} ({order.billing_email})")
        print(f"📊 Current Status: {order.get_status_display()}")
        print()
        
        # Test status changes
        status_sequence = ['processing', 'shipped', 'delivered']
        
        for new_status in status_sequence:
            if order.status != new_status:
                print(f"🔄 Changing status to: {new_status}")
                
                # Store original status for signal
                order._original_status = order.status
                
                # Change status
                order.status = new_status
                order.save()
                
                print(f"✅ Status changed to {order.get_status_display()}")
                print(f"📧 Email should be sent to {order.billing_email}")
                print("-" * 30)
        
        print("\n🎉 Test completed!")
        print("📧 Check the email logs and recipient inbox for status emails.")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()


def test_email_templates():
    """Test email template rendering"""
    
    print("\n🎨 Testing Email Template Rendering")
    print("=" * 50)
    
    from django.template.loader import render_to_string
    
    try:
        # Get a test order
        order = Order.objects.first()
        if not order:
            print("❌ No orders found for template testing")
            return
        
        # Mock request object
        class MockRequest:
            def __init__(self):
                self.scheme = 'https'
            
            def get_host(self):
                return 'oraagh.com'
        
        context = {
            'order': order,
            'user': order.user,
            'request': MockRequest(),
        }
        
        templates = [
            ('processing', 'orders/email/order_status_processing.html'),
            ('shipped', 'orders/email/order_status_shipped.html'),
            ('delivered', 'orders/email/order_status_delivered.html'),
            ('cancelled', 'orders/email/order_status_cancelled.html'),
        ]
        
        for status, template_path in templates:
            try:
                html_content = render_to_string(template_path, context)
                print(f"✅ {status.title()} template rendered successfully")
            except Exception as e:
                print(f"❌ {status.title()} template error: {str(e)}")
        
        print("\n🎉 Template testing completed!")
        
    except Exception as e:
        print(f"❌ Error during template testing: {str(e)}")


if __name__ == "__main__":
    print("🚀 Starting Order Status Email Tests\n")
    
    # Test email templates first
    test_email_templates()
    
    # Test actual status changes
    test_order_status_emails()
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print("• Email templates tested for rendering")
    print("• Order status changes tested")
    print("• Check Django logs for email sending status")
    print("• Check recipient email inbox for actual emails")
    print("\n💡 To run this test:")
    print("   python test_order_status_emails.py")
