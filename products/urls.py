from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('<slug:product_slug>/submit-review/', views.submit_review, name='submit_review'),
    path('<slug:product_slug>/request-deal/', views.request_deal, name='request_deal'),
]
