from django.urls import path
from .views import TermsOfUseView, PrivacyPolicyView, CookiePolicyView, AboutView
from . import views

app_name = 'core'

urlpatterns = [
    path('terms-of-use/', TermsOfUseView.as_view(), name='terms_of_use'),
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('cookie-policy/', CookiePolicyView.as_view(), name='cookie_policy'),
    path('about/', AboutView.as_view(), name='about'),
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
]