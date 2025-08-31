from django import forms
from products.models import Product, ProductCategory, Review
from blog.models import Post
from newsletter.models import Subscriber

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'sku', 'price', 'stock_quantity', 'product_type', 'weight', 'weight_unit', 'brand', 'origin_country', 'condition', 'is_featured', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-amber-700 focus:border-amber-700'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-amber-700 focus:border-amber-700', 'rows': 5}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-amber-700 focus:border-amber-700'}),
            'sku': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-amber-700 focus:border-amber-700'}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-amber-700 focus:border-amber-700'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-amber-700 focus:border-amber-700'}),
            'product_type': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-amber-700 focus:border-amber-700'}),
            'weight': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-amber-700 focus:border-amber-700'}),
            'weight_unit': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-amber-700 focus:border-amber-700'}),
            'brand': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-amber-700 focus:border-amber-700'}),
            'origin_country': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-amber-700 focus:border-amber-700'}),
            'condition': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-amber-700 focus:border-amber-700'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-amber-700 focus:border-amber-700'}),
        }

# ReportForm removed - reports app no longer in use

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'featured_image', 'status', 'categories', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-amber-700 focus:border-amber-700'}),
            'content': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-amber-700 focus:border-amber-700', 'rows': 10}),
            'featured_image': forms.FileInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-amber-700 focus:border-amber-700'}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-amber-700 focus:border-amber-700'}),
            'categories': forms.SelectMultiple(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-amber-700 focus:border-amber-700', 'size': 5}),
            'tags': forms.SelectMultiple(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-amber-700 focus:border-amber-700', 'size': 5}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['product', 'author', 'email', 'rating', 'comment', 'status']
        widgets = {
            'product': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-amber-700 focus:border-amber-700'}),
            'author': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-amber-700 focus:border-amber-700'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-amber-700 focus:border-amber-700'}),
            'rating': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-amber-700 focus:border-amber-700'}),
            'comment': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-amber-700 focus:border-amber-700', 'rows': 5}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-amber-700 focus:border-amber-700'}),
        }

class NewsletterForm(forms.Form):
    subject = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 border border-amber-200 bg-amber-50 text-amber-900 rounded-lg focus:ring-2 focus:ring-amber-700 focus:border-amber-700 transition',
            'placeholder': 'Enter email subject'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2.5 border border-amber-200 bg-amber-50 text-amber-900 rounded-lg focus:ring-2 focus:ring-amber-700 focus:border-amber-700 transition',
            'rows': 12,
            'placeholder': 'Compose your newsletter...'
        })
    )
