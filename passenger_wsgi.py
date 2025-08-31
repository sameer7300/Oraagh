import os
import sys

# Hardcode the project path for the production environment
project_path = '/home1/oraaghco/oraagh'
if project_path not in sys.path:
    sys.path.insert(0, project_path)


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'production_settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
