from django.urls import path
from . import views

app_name = 'newsletter'

urlpatterns = [
    path('', views.newsletter_home, name='newsletter_home'),
    path('subscribe/', views.subscribe, name='subscribe'),

]