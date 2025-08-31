from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Test Django email configuration'

    def handle(self, *args, **options):
        self.stdout.write("Testing Django email configuration...")
        
        # Print current settings
        self.stdout.write(f"EMAIL_HOST: {settings.EMAIL_HOST}")
        self.stdout.write(f"EMAIL_PORT: {settings.EMAIL_PORT}")
        self.stdout.write(f"EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
        self.stdout.write(f"EMAIL_HOST_USER: {os.getenv('EMAIL_HOST_USER')}")
        self.stdout.write(f"EMAIL_HOST_PASSWORD: {'*' * len(os.getenv('EMAIL_HOST_PASSWORD', '')) if os.getenv('EMAIL_HOST_PASSWORD') else 'NOT SET'}")
        self.stdout.write(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        
        try:
            # Send test email
            subject = 'Django SMTP Test - ORAAGH'
            text_content = 'This is a test email from Django using ORAAGH SMTP settings.'
            html_content = '<p>This is a test email from Django using <strong>ORAAGH</strong> SMTP settings.</p>'
            
            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [os.getenv('EMAIL_HOST_USER')]  # Send to self
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            self.stdout.write(self.style.SUCCESS('✅ Django email sent successfully!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Django email error: {e}'))
