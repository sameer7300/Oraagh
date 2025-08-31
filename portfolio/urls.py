from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.portfolio_home, name='portfolio_home'),
    path('lease/<slug:slug>/', views.lease_detail, name='lease_detail'),
    path('lease/<slug:slug>/pdf/', views.lease_pdf, name='lease_pdf'),
    path('map/', views.map_view, name='map_view'),
    path('team/', views.team, name='team'),
    path('team/<int:pk>/', views.team_member_detail, name='team_member_detail'),
]