from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full py-3 pl-12 pr-4 bg-transparent text-gray-700 placeholder-gray-500 focus:outline-none',
        'placeholder': 'Full Name'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'w-full py-3 pl-12 pr-4 bg-transparent text-gray-700 placeholder-gray-500 focus:outline-none',
        'placeholder': 'Email Address'
    }))
    subject = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full py-3 pl-12 pr-4 bg-transparent text-gray-700 placeholder-gray-500 focus:outline-none',
        'placeholder': 'Subject'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'w-full py-3 px-4 bg-transparent text-gray-700 placeholder-gray-500 focus:outline-none',
        'placeholder': 'Your Message',
        'rows': 5
    }))
