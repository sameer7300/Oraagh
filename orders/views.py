from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal
from django.utils import timezone
from .models import Cart, CartItem, Order, OrderItem, AbandonedCart
from products.models import Product
from core.models import DeliveryCharge
import json

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    context = {
        'cart': cart,
        'cart_items': cart.items.all(),
        'cart_total': cart.get_total(),
        'cart_count': cart.get_total_items(),
        'delivery_charges': DeliveryCharge.objects.filter(is_active=True).order_by('charge'),
        'default_delivery': DeliveryCharge.get_default(),
    }
    return render(request, 'orders/cart.html', context)

def update_abandoned_cart_tracking(user, cart):
    """Update or create abandoned cart tracking record"""
    if not cart.items.exists():
        return
    
    # Create cart items snapshot
    cart_items_snapshot = []
    for item in cart.items.all():
        cart_items_snapshot.append({
            'product_id': item.product.id,
            'product_name': item.product.name,
            'product_price': str(item.product.price),
            'quantity': item.quantity,
            'subtotal': str(item.get_subtotal()),
            'product_image': item.product.media.first().media_file.url if item.product.media.first() else None,
        })
    
    # Update or create abandoned cart record
    abandoned_cart, created = AbandonedCart.objects.get_or_create(
        user=user,
        is_recovered=False,
        defaults={
            'stage': 'cart',
            'cart_items_snapshot': cart_items_snapshot,
            'cart_total': cart.get_total(),
            'cart_created_at': cart.created_at,
            'last_activity_at': timezone.now(),
        }
    )
    
    if not created:
        # Update existing record
        abandoned_cart.cart_items_snapshot = cart_items_snapshot
        abandoned_cart.cart_total = cart.get_total()
        abandoned_cart.last_activity_at = timezone.now()
        abandoned_cart.stage = 'cart'  # Reset to cart stage if user goes back to cart
        abandoned_cart.save()

def track_checkout_abandonment(user, cart):
    """Track when user starts checkout process"""
    if not cart.items.exists():
        return
    
    # Create cart items snapshot
    cart_items_snapshot = []
    for item in cart.items.all():
        cart_items_snapshot.append({
            'product_id': item.product.id,
            'product_name': item.product.name,
            'product_price': str(item.product.price),
            'quantity': item.quantity,
            'subtotal': str(item.get_subtotal()),
            'product_image': item.product.media.first().media_file.url if item.product.media.first() else None,
        })
    
    # Update or create abandoned cart record for checkout stage
    abandoned_cart, created = AbandonedCart.objects.get_or_create(
        user=user,
        is_recovered=False,
        defaults={
            'stage': 'checkout',
            'cart_items_snapshot': cart_items_snapshot,
            'cart_total': cart.get_total(),
            'cart_created_at': cart.created_at,
            'last_activity_at': timezone.now(),
            'checkout_started_at': timezone.now(),
        }
    )
    
    if not created:
        # Update existing record to checkout stage
        abandoned_cart.cart_items_snapshot = cart_items_snapshot
        abandoned_cart.cart_total = cart.get_total()
        abandoned_cart.last_activity_at = timezone.now()
        abandoned_cart.stage = 'checkout'
        abandoned_cart.checkout_started_at = timezone.now()
        abandoned_cart.save()

def mark_cart_as_recovered(user):
    """Mark abandoned cart as recovered when order is placed"""
    AbandonedCart.objects.filter(
        user=user,
        is_recovered=False
    ).update(
        is_recovered=True,
        recovered_at=timezone.now()
    )

@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    quantity = int(request.POST.get('quantity', 1))
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    # Update abandoned cart tracking
    update_abandoned_cart_tracking(request.user, cart)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart',
            'cart_count': cart.get_total_items()
        })
    
    messages.success(request, f'{product.name} has been added to your cart.')
    return redirect('products:product_detail', slug=product.slug)

@login_required
@require_POST
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Cart updated successfully.')
    else:
        cart_item.delete()
        messages.success(request, 'Item removed from cart.')
    
    # Update abandoned cart tracking
    cart = Cart.objects.get(user=request.user)
    update_abandoned_cart_tracking(request.user, cart)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Cart updated successfully.',
            'cart_count': cart.get_total_items(),
            'cart_total': str(cart.get_total())
        })
    
    return redirect('orders:cart')

@login_required
@require_POST
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} has been removed from your cart.')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = Cart.objects.get(user=request.user)
        return JsonResponse({
            'success': True,
            'cart_count': cart.get_total_items()
        })
    
    return redirect('orders:cart')

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('products:product_list')
    
    # Track checkout abandonment
    track_checkout_abandonment(request.user, cart)
    
    if request.method == 'POST':
        # Create order
        order = Order.objects.create(
            user=request.user,
            billing_name=request.POST.get('billing_name'),
            billing_email=request.POST.get('billing_email'),
            billing_phone=request.POST.get('billing_phone'),
            billing_address=request.POST.get('billing_address'),
            billing_city=request.POST.get('billing_city'),
            billing_state=request.POST.get('billing_state'),
            billing_zip=request.POST.get('billing_zip'),
            billing_country=request.POST.get('billing_country'),
            shipping_name=request.POST.get('shipping_name', request.POST.get('billing_name')),
            shipping_address=request.POST.get('shipping_address', request.POST.get('billing_address')),
            shipping_city=request.POST.get('shipping_city', request.POST.get('billing_city')),
            shipping_state=request.POST.get('shipping_state', request.POST.get('billing_state')),
            shipping_zip=request.POST.get('shipping_zip', request.POST.get('billing_zip')),
            shipping_country=request.POST.get('shipping_country', request.POST.get('billing_country')),
            subtotal=cart.get_total(),
            total=cart.get_total(),  # Add tax and shipping calculation if needed
            customer_notes=request.POST.get('customer_notes', ''),
            payment_method=request.POST.get('payment_method', 'Cash on Delivery'),
        )
        
        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
            )
        
        # Mark abandoned cart as recovered
        mark_cart_as_recovered(request.user)
        
        # Clear cart
        cart.items.all().delete()
        
        # Send confirmation email to customer
        try:
            subject = f'Order Confirmation - {order.order_number}'
            
            # Render HTML email
            html_message = render_to_string('orders/email/order_confirmation.html', {
                'order': order,
                'user': request.user,
                'request': request,
            })
            
            # Render plain text fallback
            plain_message = render_to_string('orders/email/order_confirmation.txt', {
                'order': order,
                'user': request.user,
                'request': request,
            })
            
            from django.core.mail import EmailMultiAlternatives
            
            msg = EmailMultiAlternatives(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [order.billing_email]
            )
            msg.attach_alternative(html_message, "text/html")
            msg.send(fail_silently=False)
            
            print(f"Customer email sent successfully to {order.billing_email}")
        except Exception as e:
            print(f"Error sending customer email: {e}")
            # Log more details for debugging
            import traceback
            print(f"Full error traceback: {traceback.format_exc()}")
        
        # Send notification email to admin
        try:
            admin_subject = f'New Order Received - {order.order_number}'
            
            # Render HTML email
            admin_html_message = render_to_string('orders/email/admin_order_notification.html', {
                'order': order,
                'user': request.user,
                'request': request,
            })
            
            # Render plain text fallback
            admin_plain_message = render_to_string('orders/email/admin_order_notification.txt', {
                'order': order,
                'user': request.user,
                'request': request,
            })
            
            # Get admin email from settings or use a default
            admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@uniqueantique.pk')
            
            from django.core.mail import EmailMultiAlternatives
            
            admin_msg = EmailMultiAlternatives(
                admin_subject,
                admin_plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [admin_email]
            )
            admin_msg.attach_alternative(admin_html_message, "text/html")
            admin_msg.send(fail_silently=False)
            
            print(f"Admin email sent successfully to {admin_email}")
        except Exception as e:
            print(f"Error sending admin email: {e}")
            # Log more details for debugging
            import traceback
            print(f"Full admin email error traceback: {traceback.format_exc()}")
        
        messages.success(request, f'Your order {order.order_number} has been placed successfully!')
        return redirect('accounts:order_detail', order_id=order.id)
    
    # Pre-fill form with user profile data
    try:
        profile = request.user.profile
        initial_data = {
            'billing_name': request.user.get_full_name(),
            'billing_email': request.user.email,
            'billing_phone': profile.phone,
            'billing_address': profile.address,
            'billing_city': profile.city,
            'billing_state': profile.state,
            'billing_zip': profile.zip_code,
            'billing_country': profile.country,
            # Pre-fill shipping with same data
            'shipping_name': request.user.get_full_name(),
            'shipping_address': profile.address,
            'shipping_city': profile.city,
            'shipping_state': profile.state,
            'shipping_zip': profile.zip_code,
            'shipping_country': profile.country,
        }
    except:
        initial_data = {
            'billing_name': request.user.get_full_name(),
            'billing_email': request.user.email,
            'shipping_name': request.user.get_full_name(),
        }
    
    context = {
        'cart': cart,
        'cart_items': cart.items.all(),
        'cart_total': cart.get_total(),
        'initial_data': initial_data,
    }
    return render(request, 'orders/checkout.html', context)
