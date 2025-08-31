from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from .forms import SignUpForm, UserProfileForm, UserUpdateForm
from .models import UserProfile, PasswordResetCode, EmailVerificationCode
from orders.models import Order

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Create user but don't activate yet
            user = form.save(commit=False)
            user.is_active = False  # User must verify email first
            user.save()
            
            # Create user profile with optional fields from form
            profile_data = {
                'phone': request.POST.get('phone', ''),
                'city': request.POST.get('city', ''),
                'country': request.POST.get('country', ''),
            }
            # Remove empty values
            profile_data = {k: v for k, v in profile_data.items() if v.strip()}
            
            # Update user profile with optional fields (profile already created by signal)
            if profile_data:
                profile = user.profile
                for key, value in profile_data.items():
                    setattr(profile, key, value)
                profile.save()
            
            # Create verification code
            verification_code = EmailVerificationCode.objects.create(user=user)
            
            # Send verification email
            try:
                from django.template.loader import render_to_string
                from django.core.mail import EmailMultiAlternatives
                
                subject = 'Verify Your Email - Timeless Cart'
                
                # Render HTML template
                html_content = render_to_string('accounts/email/email_verification_code.html', {
                    'user': user,
                    'code': verification_code.code,
                    'request': request,
                })
                
                # Plain text fallback
                text_content = f"""
Hello {user.first_name or user.username},

Welcome to Timeless Cart! To complete your account registration, please verify your email address.

Your 6-digit verification code is: {verification_code.code}

This code will expire in 30 minutes.

If you didn't create an account with Timeless Cart, please ignore this email.

Best regards,
Timeless Cart Team
                """
                
                # Create email with both HTML and text versions
                email = EmailMultiAlternatives(
                    subject,
                    text_content,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email]
                )
                email.attach_alternative(html_content, "text/html")
                email.send()
                
                # Store user ID in session for verification step
                request.session['verification_user_id'] = user.id
                messages.success(request, f'Account created! Please check your email ({user.email}) for a verification code.')
                return redirect('accounts:verify_email')
                
            except Exception as e:
                # If email fails, delete the user and show error
                user.delete()
                messages.error(request, 'Failed to send verification email. Please try again.')
                return render(request, 'accounts/signup.html', {'form': form})
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if username_or_email and password:
            # First, find the user object to check if they exist and their status
            user_obj = None
            if '@' in username_or_email:
                # It's an email
                try:
                    user_obj = User.objects.get(email=username_or_email)
                except User.DoesNotExist:
                    pass
            else:
                # It's a username
                try:
                    user_obj = User.objects.get(username=username_or_email)
                except User.DoesNotExist:
                    pass
            
            if user_obj:
                # User exists, now check password manually since authenticate() fails for inactive users
                from django.contrib.auth.hashers import check_password
                
                if check_password(password, user_obj.password):
                    # Password is correct
                    if user_obj.is_active:
                        # Use authenticate for active users to get proper user object
                        user = authenticate(username=user_obj.username, password=password)
                        login(request, user)
                        display_name = user_obj.first_name or user_obj.username
                        messages.success(request, f'Welcome back, {display_name}!')
                        next_page = request.GET.get('next', 'core:home')
                        return redirect(next_page)
                    else:
                        # User exists, password correct, but account is not verified
                        request.session['verification_user_id'] = user_obj.id
                        messages.warning(request, 'Your account is not verified. Please check your email and enter the verification code to activate your account.')
                        return redirect('accounts:verify_email')
                else:
                    # User exists but password is wrong
                    messages.error(request, 'Incorrect password. Please try again.')
            else:
                # User doesn't exist
                messages.error(request, 'No account found with this email/username. Please check your details or sign up for a new account.')
        else:
            messages.error(request, 'Please enter both email/username and password.')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('core:home')

@login_required
def profile_view(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    
    # Get user's orders
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Get active orders (not delivered or cancelled) for tracking display
    active_orders = Order.objects.filter(
        user=request.user,
        status__in=['pending', 'processing', 'shipped']
    ).order_by('-created_at')
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'orders': orders,
        'active_orders': active_orders,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def order_history(request):
    from django.core.paginator import Paginator
    from django.db.models import Sum, Count
    
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Calculate statistics
    total_orders = orders.count()
    total_items = orders.aggregate(total_items=Sum('items__quantity'))['total_items'] or 0
    total_spent = orders.aggregate(total_spent=Sum('total'))['total_spent'] or 0
    
    # Pagination
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'orders': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'total_orders': total_orders,
        'total_items': total_items,
        'total_spent': total_spent,
    }
    return render(request, 'accounts/order_history.html', context)

@login_required
def order_detail(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('accounts:order_history')
    
    return render(request, 'accounts/order_detail.html', {'order': order})


def forgot_password_view(request):
    """Request password reset - send 6-digit code to email"""
    if request.method == 'POST':
        email_or_username = request.POST.get('email_or_username', '').strip()
        
        if not email_or_username:
            messages.error(request, 'Please enter your email or username.')
            return render(request, 'accounts/forgot_password.html')
        
        # Try to find user by email or username
        user = None
        try:
            if '@' in email_or_username:
                user = User.objects.get(email=email_or_username)
            else:
                user = User.objects.get(username=email_or_username)
        except User.DoesNotExist:
            # Don't reveal if user exists or not for security
            messages.success(request, 'If an account with that email/username exists, you will receive a password reset code shortly.')
            return render(request, 'accounts/forgot_password.html')
        
        if not user.email:
            messages.error(request, 'No email address associated with this account.')
            return render(request, 'accounts/forgot_password.html')
        
        # Invalidate any existing codes for this user
        PasswordResetCode.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Create new reset code
        reset_code = PasswordResetCode.objects.create(user=user)
        
        # Send email with code using HTML template
        try:
            from django.template.loader import render_to_string
            from django.core.mail import EmailMultiAlternatives
            
            subject = 'Password Reset Code - Timeless Cart'
            
            # Render HTML template
            html_content = render_to_string('accounts/email/password_reset_code.html', {
                'user': user,
                'code': reset_code.code,
                'request': request,
            })
            
            # Plain text fallback
            text_content = f"""
Hello {user.first_name or user.username},

You requested a password reset for your Timeless Cart account.

Your 6-digit verification code is: {reset_code.code}

This code will expire in 15 minutes.

If you didn't request this password reset, please ignore this email.

Best regards,
Timeless Cart Team
            """
            
            # Create email with both HTML and text versions
            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            # Store user ID in session for verification step
            request.session['reset_user_id'] = user.id
            messages.success(request, f'A 6-digit verification code has been sent to {user.email}')
            return redirect('accounts:verify_reset_code')
            
        except Exception as e:
            messages.error(request, 'Failed to send email. Please try again later.')
            return render(request, 'accounts/forgot_password.html')
    
    return render(request, 'accounts/forgot_password.html')


def verify_reset_code_view(request):
    """Verify the 6-digit code and allow password reset"""
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, 'Session expired. Please request a new password reset.')
        return redirect('accounts:forgot_password')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Invalid session. Please request a new password reset.')
        return redirect('accounts:forgot_password')
    
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        
        if not code:
            messages.error(request, 'Please enter the verification code.')
            return render(request, 'accounts/verify_reset_code.html', {'user': user})
        
        # Find valid reset code
        try:
            reset_code = PasswordResetCode.objects.get(
                user=user,
                code=code,
                is_used=False
            )
            
            if not reset_code.is_valid():
                messages.error(request, 'This code has expired. Please request a new password reset.')
                return redirect('accounts:forgot_password')
            
            # Mark code as used
            reset_code.is_used = True
            reset_code.save()
            
            # Store verification in session
            request.session['verified_reset_user_id'] = user.id
            request.session['reset_code_verified'] = True
            
            messages.success(request, 'Code verified successfully! Please set your new password.')
            return redirect('accounts:reset_password')
            
        except PasswordResetCode.DoesNotExist:
            messages.error(request, 'Invalid verification code. Please try again.')
            return render(request, 'accounts/verify_reset_code.html', {'user': user})
    
    return render(request, 'accounts/verify_reset_code.html', {'user': user})


def reset_password_view(request):
    """Set new password after code verification"""
    user_id = request.session.get('verified_reset_user_id')
    code_verified = request.session.get('reset_code_verified')
    
    if not user_id or not code_verified:
        messages.error(request, 'Please verify your reset code first.')
        return redirect('accounts:forgot_password')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Invalid session. Please request a new password reset.')
        return redirect('accounts:forgot_password')
    
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            
            # Clear session data
            request.session.pop('reset_user_id', None)
            request.session.pop('verified_reset_user_id', None)
            request.session.pop('reset_code_verified', None)
            
            messages.success(request, 'Your password has been reset successfully! Please log in with your new password.')
            return redirect('accounts:login')
    else:
        form = SetPasswordForm(user)
    
    return render(request, 'accounts/reset_password.html', {'form': form, 'user': user})


def resend_reset_code_view(request):
    """Resend password reset code via AJAX"""
    if request.method == 'POST':
        user_id = request.session.get('reset_user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': 'Session expired.'})
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found.'})
        
        # Check if user has requested too many codes recently (rate limiting)
        recent_codes = PasswordResetCode.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timezone.timedelta(minutes=5)
        ).count()
        
        if recent_codes >= 3:
            return JsonResponse({'success': False, 'message': 'Too many requests. Please wait 5 minutes before requesting another code.'})
        
        # Invalidate existing codes
        PasswordResetCode.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Create new code
        reset_code = PasswordResetCode.objects.create(user=user)
        
        # Send email using HTML template
        try:
            from django.template.loader import render_to_string
            from django.core.mail import EmailMultiAlternatives
            
            subject = 'New Password Reset Code - Timeless Cart'
            
            # Render HTML template
            html_content = render_to_string('accounts/email/password_reset_code.html', {
                'user': user,
                'code': reset_code.code,
                'request': request,
            })
            
            # Plain text fallback
            text_content = f"""
Hello {user.first_name or user.username},

Here is your new 6-digit verification code: {reset_code.code}

This code will expire in 15 minutes.

Best regards,
Timeless Cart Team
            """
            
            # Create email with both HTML and text versions
            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            return JsonResponse({'success': True, 'message': 'New verification code sent successfully!'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Failed to send email. Please try again.'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


def verify_email_view(request):
    """Verify email address with 6-digit code"""
    user_id = request.session.get('verification_user_id')
    
    if not user_id:
        messages.error(request, 'Session expired. Please register again.')
        return redirect('accounts:signup')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Invalid session. Please register again.')
        return redirect('accounts:signup')
    
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        
        if not code:
            messages.error(request, 'Please enter the verification code.')
            return render(request, 'accounts/verify_email.html', {'user': user})
        
        # Find valid verification code
        try:
            verification_code = EmailVerificationCode.objects.get(
                user=user,
                code=code,
                is_used=False
            )
            
            if not verification_code.is_valid():
                messages.error(request, 'This code has expired. Please request a new verification code.')
                return render(request, 'accounts/verify_email.html', {'user': user})
            
            # Mark code as used and activate user
            verification_code.is_used = True
            verification_code.save()
            
            user.is_active = True
            user.save()
            
            # Clear session data
            request.session.pop('verification_user_id', None)
            
            # Log the user in
            login(request, user)
            
            messages.success(request, f'Welcome to Timeless Cart, {user.username}! Your email has been verified and your account is now active.')
            
            # Force redirect to home page
            from django.http import HttpResponseRedirect
            from django.urls import reverse
            return HttpResponseRedirect(reverse('core:home'))
            
        except EmailVerificationCode.DoesNotExist:
            messages.error(request, 'Invalid verification code. Please try again.')
            return render(request, 'accounts/verify_email.html', {'user': user})
    
    return render(request, 'accounts/verify_email.html', {'user': user})


def resend_verification_code_view(request):
    """Resend email verification code via AJAX"""
    if request.method == 'POST':
        user_id = request.session.get('verification_user_id')
        if not user_id:
            return JsonResponse({'success': False, 'message': 'Session expired.'})
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found.'})
        
        # Check if user has requested too many codes recently (rate limiting)
        recent_codes = EmailVerificationCode.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timezone.timedelta(minutes=5)
        ).count()
        
        if recent_codes >= 3:
            return JsonResponse({'success': False, 'message': 'Too many requests. Please wait 5 minutes before requesting another code.'})
        
        # Invalidate existing codes
        EmailVerificationCode.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Create new code
        verification_code = EmailVerificationCode.objects.create(user=user)
        
        # Send email
        try:
            from django.template.loader import render_to_string
            from django.core.mail import EmailMultiAlternatives
            
            subject = 'New Email Verification Code - Timeless Cart'
            
            # Render HTML template
            html_content = render_to_string('accounts/email/email_verification_code.html', {
                'user': user,
                'code': verification_code.code,
                'request': request,
            })
            
            # Plain text fallback
            text_content = f"""
Hello {user.first_name or user.username},

Here is your new 6-digit verification code: {verification_code.code}

This code will expire in 30 minutes.

Best regards,
Timeless Cart Team
            """
            
            # Create email with both HTML and text versions
            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            return JsonResponse({'success': True, 'message': 'New verification code sent successfully!'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Failed to send email. Please try again.'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})
