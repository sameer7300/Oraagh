from django import forms
from .models import Subscriber

class NewsletterCreationForm(forms.Form):
    subject = forms.CharField(max_length=200)
    message = forms.CharField(widget=forms.Textarea)

class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ('email',)
        widgets = {
            'email': forms.EmailInput(
                attrs={
                    'class': 'w-full px-4 py-2 text-gray-700 bg-gray-200 rounded-l-md focus:outline-none focus:ring-2 focus:ring-red-500',
                    'placeholder': 'Enter your email...',
                    'aria-label': 'Email for newsletter'
                }
            )
        }
