from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .forms import SubscriberForm, NewsletterCreationForm
from .models import Subscriber
from django.utils.html import strip_tags
from django.http import JsonResponse

def subscribe(request):
    if request.method == 'POST':
        form = SubscriberForm(request.POST)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if form.is_valid():
            form.save()
            if is_ajax:
                return JsonResponse({'status': 'success', 'message': 'Thank you for subscribing!'})
            else:
                messages.success(request, 'Thank you for subscribing to our newsletter!')
        else:
            error_message = form.errors.get('__all__', ['This email is either invalid or already subscribed.'])[0]
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': error_message}, status=400)
            else:
                messages.error(request, error_message)
    
    return redirect(request.META.get('HTTP_REFERER', '/'))

def compose_newsletter_view(request):
    if request.method == 'POST':
        form = NewsletterCreationForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            subscribers = Subscriber.objects.all()
            recipient_list = [subscriber.email for subscriber in subscribers]

            logo_url = request.build_absolute_uri(settings.MEDIA_URL + 'red_sun_logo.png')

            html_content = render_to_string('newsletter/email/newsletter_template.html', {
                'subject': subject,
                'message': message,
                'logo_url': logo_url,
            })
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            messages.success(request, 'Newsletter sent successfully!')
            return redirect('admin:newsletter_subscriber_changelist')
    else:
        form = NewsletterCreationForm()
        
    return render(request, 'newsletter/compose_newsletter.html', {'form': form})


def newsletter_home(request):
    return render(request, 'newsletter/home.html')
