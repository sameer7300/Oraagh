"""
WSGI config for production deployment on HosterPK
"""

import os
from django.core.wsgi import get_wsgi_application

# Set the settings module for production
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'production_settings')

application = get_wsgi_application()
