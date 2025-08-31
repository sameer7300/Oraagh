from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.views.generic import ListView, DetailView
from django.db.models import Avg, Q
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
import json
from .models import Product, ProductCategory, Review
from .forms import DealRequestForm
from core.models import DeliveryCharge

class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Searching
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(sku__icontains=search_query)
            )

        # Filtering
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        product_type = self.request.GET.get('product_type')
        if product_type:
            queryset = queryset.filter(product_type=product_type)

        # Sorting
        sort_by = self.request.GET.get('sort')
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'name_asc':
            queryset = queryset.order_by('name')
        elif sort_by == 'name_desc':
            queryset = queryset.order_by('-name')
        else:
            # If no sort order is specified, shuffle the products.
            queryset = queryset.order_by('?')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ProductCategory.objects.all()
        context['product_types'] = Product.PRODUCT_TYPE_CHOICES
        context['current_category'] = self.request.GET.get('category', '')
        context['current_product_type'] = self.request.GET.get('product_type', '')
        context['current_sort'] = self.request.GET.get('sort', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        approved_reviews = product.reviews.filter(status='Approved')
        
        # Add integer rating for template loop
        for review in approved_reviews:
            review.rating_int = int(round(review.rating))
        context['approved_reviews'] = approved_reviews
        context['review_count'] = approved_reviews.count()
        context['deal_form'] = DealRequestForm()
        
        # Calculate average rating
        average_rating = approved_reviews.aggregate(Avg('rating'))['rating__avg']
        context['average_rating'] = average_rating
        context['average_rating_int'] = int(round(average_rating)) if average_rating else 0

        media_urls = [media.media_file.url for media in product.media.all()]
        context['media_urls_json'] = json.dumps(media_urls, cls=DjangoJSONEncoder)

        if product.category:
            context['related_products'] = Product.objects.filter(category=product.category).exclude(pk=product.pk)[:4]
        else:
            context['related_products'] = Product.objects.none()

        # Add delivery charges
        context['delivery_charges'] = DeliveryCharge.objects.filter(is_active=True).order_by('charge')
        context['default_delivery'] = DeliveryCharge.get_default()

        return context

def submit_review(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    if request.method == 'POST':
        author = request.POST.get('author')
        email = request.POST.get('email')
        comment = request.POST.get('comment')
        rating = request.POST.get('rating')

        if author and email and comment and rating:
            new_review = Review.objects.create(
                product=product,
                author=author,
                email=email,
                comment=comment,
                rating=int(rating),
                status='Pending'  # Reviews await approval
            )

            logo_url = request.build_absolute_uri(settings.MEDIA_URL + 'red_sun_logo.png')

            # --- Send confirmation email to user ---
            user_context = {
                'product': product,
                'user': {'username': author},
                'logo_url': logo_url,
            }
            html_content_user = render_to_string('products/email/review_submitted_user.html', user_context)
            text_content_user = strip_tags(html_content_user)
            email_user = EmailMultiAlternatives(
                'We\'ve Received Your Review!',
                text_content_user,
                settings.DEFAULT_FROM_EMAIL,
                [email]
            )
            email_user.attach_alternative(html_content_user, "text/html")
            email_user.send()

            # --- Send notification email to admin ---
            admin_emails = [admin[1] for admin in settings.ADMINS]
            if admin_emails:
                admin_url = request.build_absolute_uri(reverse('admin:products_review_change', args=[new_review.id]))
                admin_context = {
                    'product': product,
                    'user': {'username': author, 'email': email},
                    'rating': new_review.rating,
                    'comment': new_review.comment,
                    'admin_url': admin_url,
                    'logo_url': logo_url,
                }

                html_content_admin = render_to_string('products/email/new_review_admin.html', admin_context)
                text_content_admin = strip_tags(html_content_admin)
                email_admin = EmailMultiAlternatives(
                    f"New Review for {product.name}",
                    text_content_admin,
                    settings.DEFAULT_FROM_EMAIL,
                    admin_emails
                )
                email_admin.attach_alternative(html_content_admin, "text/html")
                email_admin.send()
            messages.success(request, 'Thank you! Your review has been submitted and is awaiting approval.')
        else:
            messages.error(request, 'Please fill out all fields to submit a review.')
    return redirect('products:product_detail', slug=product_slug)

def request_deal(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    if request.method == 'POST':
        deal_form = DealRequestForm(request.POST)
        if deal_form.is_valid():
            deal_request = deal_form.save(commit=False)
            deal_request.product = product
            
            # Send emails
            try:
                # Admin Email
                admin_emails = [admin[1] for admin in settings.ADMINS]
                logo_url = request.build_absolute_uri(settings.MEDIA_URL + 'red_sun_logo.png')
                admin_context = {
                    'product_name': product.name,
                    'product_sku': product.sku,
                    'product_url': request.build_absolute_uri(product.get_absolute_url()),
                    'user_name': deal_request.name,
                    'user_email': deal_request.email,
                    'user_phone': deal_request.phone_number,
                    'message': deal_request.message,
                    'logo_url': logo_url,
                }
                html_content_admin = render_to_string('products/email/deal_request_admin.html', admin_context)
                text_content_admin = strip_tags(html_content_admin)
                email_admin = EmailMultiAlternatives(
                    f"New Deal Request for {product.name}",
                    text_content_admin,
                    settings.DEFAULT_FROM_EMAIL,
                    admin_emails
                )
                email_admin.attach_alternative(html_content_admin, "text/html")
                email_admin.send(fail_silently=False)

                # User Email
                user_context = {
                    'product_name': product.name,
                    'product_sku': product.sku,
                    'product_url': request.build_absolute_uri(product.get_absolute_url()),
                    'user_name': deal_request.name,
                    'logo_url': logo_url,
                }
                html_content_user = render_to_string('products/email/deal_request_user.html', user_context)
                text_content_user = strip_tags(html_content_user)
                email_user = EmailMultiAlternatives(
                    'Your Deal Request has been Received',
                    text_content_user,
                    settings.DEFAULT_FROM_EMAIL,
                    [deal_request.email]
                )
                email_user.attach_alternative(html_content_user, "text/html")
                email_user.send(fail_silently=False)

                # Save the deal request after emails are sent
                deal_request.save()
                messages.success(request, 'Your deal request has been submitted successfully! We will get back to you shortly.')

            except Exception as e:
                messages.error(request, f'An error occurred while submitting your request. Please try again. Error: {e}')
            
            return redirect('products:product_detail', slug=product.slug)
        else:
            messages.error(request, 'Please provide your name and phone number.')
    return redirect('products:product_detail', slug=product_slug)
