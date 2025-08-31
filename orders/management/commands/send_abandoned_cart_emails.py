from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.conf import settings
from orders.models import AbandonedCart, Cart
from django.contrib.auth.models import User
import json


class Command(BaseCommand):
    help = 'Send abandoned cart reminder emails'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what emails would be sent without actually sending them',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No emails will be sent'))
        
        # Process cart reminders (after 2 hours)
        cart_reminders_sent = self.send_cart_reminders(dry_run)
        
        # Process checkout reminders (after 1 hour)
        checkout_reminders_sent = self.send_checkout_reminders(dry_run)
        
        # Update abandoned cart records from current carts
        self.update_abandoned_cart_records()
        
        total_sent = cart_reminders_sent + checkout_reminders_sent
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'DRY RUN: Would send {total_sent} emails '
                    f'({cart_reminders_sent} cart reminders, {checkout_reminders_sent} checkout reminders)'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully sent {total_sent} abandoned cart emails '
                    f'({cart_reminders_sent} cart reminders, {checkout_reminders_sent} checkout reminders)'
                )
            )

    def send_cart_reminders(self, dry_run=False):
        """Send cart abandonment reminders"""
        abandoned_carts = AbandonedCart.objects.filter(
            stage='cart',
            cart_reminder_sent=False,
            is_recovered=False
        )
        
        sent_count = 0
        
        for abandoned_cart in abandoned_carts:
            if abandoned_cart.should_send_cart_reminder():
                if dry_run:
                    self.stdout.write(f'Would send cart reminder to {abandoned_cart.user.email}')
                    sent_count += 1
                    continue
                
                try:
                    # Reconstruct cart items from snapshot
                    cart_items = self.reconstruct_cart_items(abandoned_cart.cart_items_snapshot)
                    
                    # Render email template
                    context = {
                        'user': abandoned_cart.user,
                        'cart_items': cart_items,
                        'cart_total': abandoned_cart.cart_total,
                        'request': self.get_request_context(),
                    }
                    
                    html_message = render_to_string('orders/email/abandoned_cart_reminder.html', context)
                    plain_message = strip_tags(html_message)
                    
                    # Send email
                    send_mail(
                        subject='Your Cart is Waiting - Oraagh',
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[abandoned_cart.user.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    
                    # Update abandoned cart record
                    abandoned_cart.cart_reminder_sent = True
                    abandoned_cart.cart_reminder_sent_at = timezone.now()
                    abandoned_cart.save()
                    
                    sent_count += 1
                    self.stdout.write(f'Sent cart reminder to {abandoned_cart.user.email}')
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to send cart reminder to {abandoned_cart.user.email}: {str(e)}')
                    )
        
        return sent_count

    def send_checkout_reminders(self, dry_run=False):
        """Send checkout abandonment reminders"""
        abandoned_carts = AbandonedCart.objects.filter(
            stage='checkout',
            checkout_reminder_sent=False,
            is_recovered=False
        )
        
        sent_count = 0
        
        for abandoned_cart in abandoned_carts:
            if abandoned_cart.should_send_checkout_reminder():
                if dry_run:
                    self.stdout.write(f'Would send checkout reminder to {abandoned_cart.user.email}')
                    sent_count += 1
                    continue
                
                try:
                    # Reconstruct cart items from snapshot
                    cart_items = self.reconstruct_cart_items(abandoned_cart.cart_items_snapshot)
                    
                    # Render email template
                    context = {
                        'user': abandoned_cart.user,
                        'cart_items': cart_items,
                        'cart_total': abandoned_cart.cart_total,
                        'request': self.get_request_context(),
                    }
                    
                    html_message = render_to_string('orders/email/abandoned_checkout_reminder.html', context)
                    plain_message = strip_tags(html_message)
                    
                    # Send email
                    send_mail(
                        subject='Complete Your Order - Oraagh',
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[abandoned_cart.user.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    
                    # Update abandoned cart record
                    abandoned_cart.checkout_reminder_sent = True
                    abandoned_cart.checkout_reminder_sent_at = timezone.now()
                    abandoned_cart.save()
                    
                    sent_count += 1
                    self.stdout.write(f'Sent checkout reminder to {abandoned_cart.user.email}')
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to send checkout reminder to {abandoned_cart.user.email}: {str(e)}')
                    )
        
        return sent_count

    def update_abandoned_cart_records(self):
        """Update abandoned cart records from current active carts"""
        # Find carts that have been inactive for at least 30 minutes
        cutoff_time = timezone.now() - timezone.timedelta(minutes=30)
        inactive_carts = Cart.objects.filter(
            updated_at__lt=cutoff_time,
            items__isnull=False
        ).distinct()
        
        for cart in inactive_carts:
            # Check if we already have an abandoned cart record for this user
            abandoned_cart, created = AbandonedCart.objects.get_or_create(
                user=cart.user,
                is_recovered=False,
                defaults={
                    'stage': 'cart',
                    'cart_items_snapshot': self.create_cart_snapshot(cart),
                    'cart_total': cart.get_total(),
                    'cart_created_at': cart.created_at,
                    'last_activity_at': cart.updated_at,
                }
            )
            
            if not created:
                # Update existing record
                abandoned_cart.cart_items_snapshot = self.create_cart_snapshot(cart)
                abandoned_cart.cart_total = cart.get_total()
                abandoned_cart.last_activity_at = cart.updated_at
                abandoned_cart.save()

    def create_cart_snapshot(self, cart):
        """Create a JSON snapshot of cart items"""
        items = []
        for item in cart.items.all():
            items.append({
                'product_id': item.product.id,
                'product_name': item.product.name,
                'product_price': str(item.product.price),
                'quantity': item.quantity,
                'subtotal': str(item.get_subtotal()),
                'product_image': item.product.media.first().media_file.url if item.product.media.first() else None,
            })
        return items

    def reconstruct_cart_items(self, cart_snapshot):
        """Reconstruct cart items from JSON snapshot for template rendering"""
        from products.models import Product
        
        items = []
        for item_data in cart_snapshot:
            try:
                product = Product.objects.get(id=item_data['product_id'])
                # Create a mock cart item object for template
                class MockCartItem:
                    def __init__(self, product, quantity, subtotal):
                        self.product = product
                        self.quantity = quantity
                        self._subtotal = subtotal
                    
                    def get_subtotal(self):
                        return self._subtotal
                
                mock_item = MockCartItem(
                    product=product,
                    quantity=item_data['quantity'],
                    subtotal=item_data['subtotal']
                )
                items.append(mock_item)
            except Product.DoesNotExist:
                # Product was deleted, skip this item
                continue
        
        return items

    def get_request_context(self):
        """Create a mock request context for template rendering"""
        class MockRequest:
            def __init__(self):
                self.scheme = 'https'
            
            def get_host(self):
                return 'oraagh.com'  # Replace with your actual domain
        
        return MockRequest()
