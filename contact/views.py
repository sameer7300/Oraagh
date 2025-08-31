from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.conf import settings
from .forms import ContactForm

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            from_email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message_body = form.cleaned_data['message']

            # Build absolute URL for the logo
            logo_url = request.build_absolute_uri(settings.MEDIA_URL + 'red_sun_logo.png')

            # Prepare context for email templates
            email_context = {
                'name': name,
                'from_email': from_email,
                'subject': subject,
                'message_body': message_body,
                'logo_url': logo_url,
            }

            try:
                # --- Render and send email to admin ---
                admin_subject = f'New Contact Form Inquiry: {subject}'
                admin_html_content = render_to_string('contact/email/admin_email.html', email_context)
                admin_text_content = f"""A new inquiry has been submitted.\nFrom: {name} <{from_email}>\nSubject: {subject}\nMessage: {message_body}"""

                admin_email = EmailMultiAlternatives(
                    admin_subject,
                    admin_text_content, # Plain-text body
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL]
                )
                admin_email.attach_alternative(admin_html_content, "text/html")
                admin_email.send()

                # --- Render and send confirmation email to user ---
                user_subject = 'We Have Received Your Message - ORAAGH'
                user_html_content = render_to_string('contact/email/user_email.html', email_context)
                user_text_content = f"""Dear {name},\n\nThank you for contacting us. We have received your message and will get back to you shortly.\n\nBest regards,\nThe ORAAGH Team"""

                user_email = EmailMultiAlternatives(
                    user_subject,
                    user_text_content, # Plain-text body
                    settings.DEFAULT_FROM_EMAIL,
                    [from_email]
                )
                user_email.attach_alternative(user_html_content, "text/html")
                user_email.send()

                messages.success(request, 'Your message has been sent successfully! If you do not receive it shortly, please check your spam/junk folder.')
                return redirect('contact:contact_view')

            except Exception as e:
                messages.error(request, f'An error occurred while sending your message: {e}')
    else:
        form = ContactForm()
    
    return render(request, 'contact/contact.html', {'form': form})

