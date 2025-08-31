from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import ProductForm, CategoryForm, PostForm, ReviewForm, NewsletterForm
from products.models import Product, ProductCategory, Review, DealRequest, ProductMedia
from blog.models import Post
from newsletter.models import Subscriber
from accounts.models import UserProfile
from orders.models import Order, Cart
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone


class DashboardLoginView(LoginView):
    template_name = 'admin_dashboard/login.html'


@login_required
def dashboard_logout(request):
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('admin_dashboard:login')

def is_staff_user(user):
    """Check if user is staff or superuser"""
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_staff_user)
def dashboard_home(request):
    from products.models import Product
    from orders.models import Order
    from django.contrib.auth.models import User
    from blog.models import Post
    
    # Get statistics
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    new_deals = 0  # Placeholder for future deals functionality
    total_customers = User.objects.filter(is_staff=False).count()
    total_blog_posts = Post.objects.count()
    
    # Get recent data
    recent_products = Product.objects.order_by('-created_at')[:5]
    recent_orders = Order.objects.order_by('-created_at')[:5]
    
    # Get order status data for chart
    order_status_data = Order.objects.values('status').annotate(count=Count('id'))
    
    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'new_deals': new_deals,
        'total_customers': total_customers,
        'total_blog_posts': total_blog_posts,
        'recent_products': recent_products,
        'recent_orders': recent_orders,
        'order_status_data': order_status_data,
    }
    
    return render(request, 'admin_dashboard/dashboard_home.html', context)


@login_required
@user_passes_test(is_staff_user)
def order_list(request):
    """List all orders with search and filter functionality"""
    from django.db.models import Sum
    
    orders_list = Order.objects.all().order_by('-created_at')

    # Calculate stats
    total_orders = orders_list.count()
    pending_orders_count = orders_list.filter(status='pending').count()
    total_revenue = orders_list.aggregate(Sum('total'))['total__sum'] or 0

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        orders_list = orders_list.filter(
            Q(order_number__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(billing_email__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(orders_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'total_orders': total_orders,
        'pending_orders_count': pending_orders_count,
        'total_revenue': total_revenue,
    }

    return render(request, 'admin_dashboard/order_list.html', context)


@login_required
@user_passes_test(is_staff_user)
def order_detail(request, order_id):
    """View order details and allow status updates"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order {order.order_number} status updated to {new_status}!')
            return redirect('admin_dashboard:order_detail', order_id=order.id)
    
    return render(request, 'admin_dashboard/order_detail.html', {'order': order})

@login_required
@user_passes_test(is_staff_user)
def product_media_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        files = request.FILES.getlist('media_files')
        for f in files:
            ProductMedia.objects.create(product=product, media_file=f)
        messages.success(request, f'{len(files)} media file(s) uploaded.')
    return redirect('admin_dashboard:product_edit', product_id=product.id)

@login_required
@user_passes_test(is_staff_user)
def product_media_delete(request, media_id):
    media = get_object_or_404(ProductMedia, id=media_id)
    product_id = media.product.id
    media.delete()
    messages.success(request, 'Media deleted.')
    return redirect('admin_dashboard:product_edit', product_id=product_id)

def customer_list(request):
    """List all customers"""
    customers_list = UserProfile.objects.filter(role='customer').order_by('-created_at')

    # Calculate stats
    total_customers = customers_list.count()

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        customers_list = customers_list.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(customers_list, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'total_customers': total_customers,
    }

    return render(request, 'admin_dashboard/customer_list.html', context)


# Team member functions removed - not needed for e-commerce site


@login_required
@user_passes_test(is_staff_user)
def content_management(request):
    """Manage website content"""
    post_count = Post.objects.count()
    review_count = Review.objects.count()
    context = {
        'post_count': post_count,
        'review_count': review_count,
    }
    return render(request, 'admin_dashboard/content_management.html', context)


@login_required
@user_passes_test(is_staff_user)
def media_management(request):
    """Manage media files"""
    media_files = ProductMedia.objects.all().order_by('-id')
    
    # Pagination
    paginator = Paginator(media_files, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    
    return render(request, 'admin_dashboard/media_management.html', context)


# Product Views
@login_required
@user_passes_test(is_staff_user)
def product_list(request):
    query = request.GET.get('q')
    product_list = Product.objects.all()
    if query:
        product_list = product_list.filter(name__icontains=query)
    paginator = Paginator(product_list, 10)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    return render(request, 'admin_dashboard/product_list.html', {'products': products, 'query': query})

@login_required
@user_passes_test(is_staff_user)
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully.')
            return redirect('admin_dashboard:product_list')
    else:
        form = ProductForm()
    return render(request, 'admin_dashboard/product_form.html', {'form': form, 'is_edit': False})

@login_required
@user_passes_test(is_staff_user)
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('admin_dashboard:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'admin_dashboard/product_form.html', {'form': form, 'is_edit': True, 'product': product})

@login_required
@user_passes_test(is_staff_user)
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('admin_dashboard:product_list')
    return render(request, 'admin_dashboard/product_confirm_delete.html', {'product': product})


@login_required
@user_passes_test(is_staff_user)
def send_newsletter(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            subscribers_emails = Subscriber.objects.values_list('email', flat=True)
            
            try:
                html_content = render_to_string('newsletter/email/newsletter_template.html', {'subject': subject, 'message': message})
                text_content = strip_tags(html_content)

                email = EmailMultiAlternatives(
                    subject,
                    text_content,
                    settings.DEFAULT_FROM_EMAIL,
                    list(subscribers_emails)
                )
                email.attach_alternative(html_content, "text/html")
                email.send()

                messages.success(request, f'Newsletter sent to {len(list(subscribers_emails))} subscribers.')
            except Exception as e:
                messages.error(request, f'An error occurred while sending the newsletter: {e}')
            
            return redirect('admin_dashboard:send_newsletter')
    else:
        form = NewsletterForm()

    # Subscriber list logic
    subscriber_list = Subscriber.objects.all().order_by('-created_at')
    search_query = request.GET.get('search', '')
    if search_query:
        subscriber_list = subscriber_list.filter(email__icontains=search_query)

    paginator = Paginator(subscriber_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'form': form,
        'subscriber_count': Subscriber.objects.count(),
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'admin_dashboard/send_newsletter.html', context)

# Category Views
@login_required
@user_passes_test(is_staff_user)
def category_list(request):
    categories = ProductCategory.objects.all()
    return render(request, 'admin_dashboard/category_list.html', {'categories': categories})

@login_required
@user_passes_test(is_staff_user)
def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
            return redirect('admin_dashboard:category_list')
    else:
        form = CategoryForm()
    return render(request, 'admin_dashboard/category_form.html', {'form': form, 'action': 'Add'})

@login_required
@user_passes_test(is_staff_user)
def category_edit(request, pk):
    category = get_object_or_404(ProductCategory, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('admin_dashboard:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'admin_dashboard/category_form.html', {'form': form, 'action': 'Edit'})

@login_required
@user_passes_test(is_staff_user)
def category_delete(request, pk):
    category = get_object_or_404(ProductCategory, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('admin_dashboard:category_list')
    return render(request, 'admin_dashboard/category_confirm_delete.html', {'category': category})

# Report Views
@login_required
@user_passes_test(is_staff_user)
def report_list(request):
    reports = Report.objects.all()
    return render(request, 'admin_dashboard/report_list.html', {'reports': reports})

@login_required
@user_passes_test(is_staff_user)
def report_add(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Report added successfully.')
            return redirect('admin_dashboard:report_list')
    else:
        form = ReportForm()
    return render(request, 'admin_dashboard/report_form.html', {'form': form, 'action': 'Add'})

@login_required
@user_passes_test(is_staff_user)
def report_edit(request, pk):
    report = get_object_or_404(Report, pk=pk)
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            form.save()
            messages.success(request, 'Report updated successfully.')
            return redirect('admin_dashboard:report_list')
    else:
        form = ReportForm(instance=report)
    return render(request, 'admin_dashboard/report_form.html', {'form': form, 'action': 'Edit'})

@login_required
@user_passes_test(is_staff_user)
def report_delete(request, pk):
    report = get_object_or_404(Report, pk=pk)
    if request.method == 'POST':
        report.delete()
        messages.success(request, 'Report deleted successfully.')
        return redirect('admin_dashboard:report_list')
    return render(request, 'admin_dashboard/report_confirm_delete.html', {'report': report})

# Post Views
@login_required
@user_passes_test(is_staff_user)
def post_list(request):
    posts = Post.objects.all()
    return render(request, 'admin_dashboard/post_list.html', {'posts': posts})

@login_required
@user_passes_test(is_staff_user)
def post_add(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m() # Needed for ManyToMany fields
            return redirect('admin_dashboard:post_list')
    else:
        form = PostForm()
    return render(request, 'admin_dashboard/post_form.html', {'form': form, 'action': 'Add'})

@login_required
@user_passes_test(is_staff_user)
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard:post_list')
    else:
        form = PostForm(instance=post)
    return render(request, 'admin_dashboard/post_form.html', {'form': form, 'action': 'Edit'})

@login_required
@user_passes_test(is_staff_user)
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        post.delete()
        return redirect('admin_dashboard:post_list')
    return render(request, 'admin_dashboard/post_confirm_delete.html', {'post': post})

# Review Views
@login_required
@user_passes_test(is_staff_user)
def review_list(request):
    reviews = Review.objects.all()
    return render(request, 'admin_dashboard/review_list.html', {'reviews': reviews})

@login_required
@user_passes_test(is_staff_user)
def review_add(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard:review_list')
    else:
        form = ReviewForm()
    return render(request, 'admin_dashboard/review_form.html', {'form': form, 'action': 'Add'})

@login_required
@user_passes_test(is_staff_user)
def review_edit(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard:review_list')
    else:
        form = ReviewForm(instance=review)
    return render(request, 'admin_dashboard/review_form.html', {'form': form, 'action': 'Edit'})

@login_required
@user_passes_test(is_staff_user)
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        review.delete()
        return redirect('admin_dashboard:review_list')
    return render(request, 'admin_dashboard/review_confirm_delete.html', {'review': review})

@login_required
@user_passes_test(is_staff_user)
def review_update_status(request, pk, status):
    review = get_object_or_404(Review, pk=pk)
    if request.method == 'POST':
        review.status = status
        review.save()
        messages.success(request, f'Review has been {status.lower()}.')
    return redirect('admin_dashboard:review_list')

# Deal Request Views
@login_required
@user_passes_test(is_staff_user)
@login_required
@user_passes_test(is_staff_user)
def product_media_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        files = request.FILES.getlist('media_files')
        for f in files:
            ProductMedia.objects.create(product=product, media_file=f)
        messages.success(request, f'{len(files)} media file(s) uploaded.')
    return redirect('admin_dashboard:product_edit', product_id=product.id)

@login_required
@user_passes_test(is_staff_user)
def product_media_delete(request, media_id):
    media = get_object_or_404(ProductMedia, id=media_id)
    product_id = media.product.id
    media.delete()
    messages.success(request, 'Media deleted.')
    return redirect('admin_dashboard:product_edit', product_id=product_id)

def deal_request_list(request):
    deals = DealRequest.objects.all().order_by('-created_at')
    return render(request, 'admin_dashboard/deal_request_list.html', {'deals': deals})

@login_required
@user_passes_test(is_staff_user)
def deal_request_detail(request, pk):
    deal = get_object_or_404(DealRequest, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['New', 'Contacted', 'Closed']:
            deal.status = new_status
            deal.save()
            messages.success(request, 'Deal status has been updated.')
            return redirect('admin_dashboard:deal_request_detail', pk=deal.pk)
    return render(request, 'admin_dashboard/deal_request_detail.html', {'deal': deal})
