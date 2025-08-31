import os
from django.views.generic import TemplateView
from django.conf import settings
from django.shortcuts import render
from django.db.models import Q
from products.models import Product, Review, ProductCategory
from blog.models import Post

# Create your views here.

class TermsOfUseView(TemplateView):
    template_name = 'core/terms_of_use.html'

class PrivacyPolicyView(TemplateView):
    template_name = 'core/privacy_policy.html'

class CookiePolicyView(TemplateView):
    template_name = 'core/cookie_policy.html'

class AboutView(TemplateView):
    template_name = 'core/about.html'


def home(request):
    """
    View for the homepage, passing featured content to the template.
    """
    # Get all products and categories, fallback to all if no featured/published items
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:8]
    if not featured_products:
        featured_products = Product.objects.filter(is_active=True)[:8]
    
    categories = ProductCategory.objects.all()[:6]
    new_arrivals = Product.objects.filter(is_active=True).order_by('-created_at')[:4]
    
    # Get published posts, fallback to all if none published
    latest_posts = Post.objects.filter(status='published').order_by('-created_at')[:3]
    if not latest_posts:
        latest_posts = Post.objects.all().order_by('-created_at')[:3]
    
    # Get approved reviews, fallback to all if none approved
    recent_reviews = Review.objects.filter(status='Approved').order_by('-created_at')[:4]
    if not recent_reviews:
        recent_reviews = Review.objects.all().order_by('-created_at')[:4]
    
    context = {
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'categories': categories,
        'latest_posts': latest_posts,
        'recent_reviews': recent_reviews,
    }
    return render(request, 'core/home.html', context)


def search(request):
    query = request.GET.get('q', '')
    product_results = []
    category_results = []
    
    if query:
        product_results = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(sku__icontains=query)
        ).distinct()

        category_results = ProductCategory.objects.filter(
            Q(name__icontains=query)
        ).distinct()

    context = {
        'query': query,
        'product_results': product_results,
        'category_results': category_results,
        'total_results': len(product_results)
    }
    return render(request, 'core/search_results.html', context)
