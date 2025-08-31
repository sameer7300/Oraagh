from django.urls import path
from . import views

app_name = 'admin_dashboard'

from .views import DashboardLoginView

urlpatterns = [
    path('login/', DashboardLoginView.as_view(), name='login'),
    path('logout/', views.dashboard_logout, name='logout'),
    path('', views.dashboard_home, name='dashboard_home'),
    
    # Order Management
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # Customer Management
    path('customers/', views.customer_list, name='customer_list'),
    
    # Content Management
    path('content/', views.content_management, name='content_management'),
    path('media/', views.media_management, name='media_management'),

    # Product URLs
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:product_id>/delete/', views.product_delete, name='product_delete'),
    path('products/<int:product_id>/media/add/', views.product_media_add, name='product_media_add'),
    path('product-media/<int:media_id>/delete/', views.product_media_delete, name='product_media_delete'),

    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    # Post URLs
    path('posts/', views.post_list, name='post_list'),
    path('posts/add/', views.post_add, name='post_add'),
    path('posts/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:pk>/delete/', views.post_delete, name='post_delete'),

    # Review URLs
    path('reviews/', views.review_list, name='review_list'),
    path('reviews/add/', views.review_add, name='review_add'),
    path('reviews/<int:pk>/edit/', views.review_edit, name='review_edit'),
    path('reviews/<int:pk>/delete/', views.review_delete, name='review_delete'),
    path('reviews/<int:pk>/status/<str:status>/', views.review_update_status, name='review_update_status'),

    # Deal Requests
    path('deal-requests/', views.deal_request_list, name='deal_request_list'),
    path('deal-requests/<int:pk>/', views.deal_request_detail, name='deal_request_detail'),

    # Newsletter
    path('newsletter/', views.send_newsletter, name='send_newsletter'),
]
