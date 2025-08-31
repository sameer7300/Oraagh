from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from .models import Subscriber
from .views import compose_newsletter_view

class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at')
    search_fields = ('email',)
    list_filter = ('created_at',)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('compose/', self.admin_site.admin_view(compose_newsletter_view), name='compose_newsletter'),
        ]
        return my_urls + urls

admin.site.register(Subscriber, SubscriberAdmin)

