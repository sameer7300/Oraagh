from django.contrib import admin, messages
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Product, ProductCategory, ProductMedia, Review, DealRequest

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

class ProductMediaInline(admin.TabularInline):
    model = ProductMedia
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'product_type', 'price', 'tax_percentage', 'get_price_with_tax_display', 'stock_quantity', 'condition', 'is_featured', 'is_active', 'created_at')
    list_filter = ('category', 'product_type', 'condition', 'is_featured', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'sku', 'brand', 'origin_country')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('get_tax_amount', 'get_price_with_tax_display')
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'category')
        }),
        ('Pricing & Tax', {
            'fields': ('price', 'tax_percentage', 'get_tax_amount', 'get_price_with_tax_display'),
            'description': 'Set the base price and tax percentage. Tax amount and total price will be calculated automatically.'
        }),
        ('Product Details', {
            'fields': ('sku', 'stock_quantity', 'product_type', 'brand', 'origin_country', 'condition')
        }),
        ('Physical Properties', {
            'fields': ('weight', 'weight_unit')
        }),
        ('E-commerce Settings', {
            'fields': ('is_featured', 'is_active')
        }),
    )
    inlines = [ProductMediaInline]
    
    def get_tax_amount(self, obj):
        """Display calculated tax amount in admin"""
        tax_amount = obj.get_tax_amount()
        if tax_amount:
            return f"PKR {tax_amount:,.2f}"
        return "PKR 0.00"
    get_tax_amount.short_description = 'Tax Amount'
    
    def get_price_with_tax_display(self, obj):
        """Display total price with tax in admin list"""
        return obj.get_price_with_tax_display()
    get_price_with_tax_display.short_description = 'Total Price (incl. Tax)'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'author', 'email', 'rating', 'status', 'created_at')
    list_filter = ('status', 'rating', 'created_at')
    search_fields = ('author', 'comment', 'product__name')
    actions = ['approve_reviews', 'reject_reviews']

    def approve_reviews(self, request, queryset):
        successful_approvals = 0
        for review in queryset:
            if review.status == 'Approved':
                continue

            if not review.email:
                review.status = 'Approved'
                review.save()
                successful_approvals += 1
                continue

            try:
                logo_url = request.build_absolute_uri(settings.MEDIA_URL + 'red_sun_logo.png')
                context = {
                    'user_name': review.author,
                    'product_name': review.product.name,
                    'product_url': request.build_absolute_uri(review.product.get_absolute_url()),
                    'logo_url': logo_url,
                }

                html_content = render_to_string('products/email/review_approved_user.html', context)
                text_content = strip_tags(html_content)

                email = EmailMultiAlternatives(
                    'Your Review has been Approved!',
                    text_content,
                    settings.DEFAULT_FROM_EMAIL,
                    [review.email]
                )
                email.attach_alternative(html_content, "text/html")
                email.send(fail_silently=False)

                # If email sends successfully, then approve the review
                review.status = 'Approved'
                review.save()
                successful_approvals += 1

            except Exception as e:
                self.message_user(
                    request,
                    f"Could not approve review by '{review.author}' because email failed to send. Error: {e}",
                    level=messages.ERROR
                )

        if successful_approvals > 0:
            self.message_user(request, f"{successful_approvals} review(s) were successfully approved.")
    approve_reviews.short_description = "Approve selected reviews and notify user"

    def reject_reviews(self, request, queryset):
        queryset.update(status='Rejected')
    reject_reviews.short_description = "Reject selected reviews"

    def save_model(self, request, obj, form, change):
        # Check if the status is being changed to 'Approved'
        if 'status' in form.changed_data and obj.status == 'Approved':
            if obj.email:
                try:
                    logo_url = request.build_absolute_uri(settings.MEDIA_URL + 'red_sun_logo.png')
                    context = {
                        'user_name': obj.author,
                        'product_name': obj.product.name,
                        'product_url': request.build_absolute_uri(obj.product.get_absolute_url()),
                        'logo_url': logo_url,
                    }
                    html_content = render_to_string('products/email/review_approved_user.html', context)
                    text_content = strip_tags(html_content)
                    email = EmailMultiAlternatives(
                        'Your Review has been Approved!',
                        text_content,
                        settings.DEFAULT_FROM_EMAIL,
                        [obj.email]
                    )
                    email.attach_alternative(html_content, "text/html")
                    email.send(fail_silently=False)
                    self.message_user(request, "Review approved and notification email sent.")
                except Exception as e:
                    self.message_user(request, f"Review was saved, but failed to send approval email. Error: {e}", level=messages.ERROR)
        super().save_model(request, obj, form, change)

@admin.register(DealRequest)
class DealRequestAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'phone_number', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'phone_number', 'product__name')
