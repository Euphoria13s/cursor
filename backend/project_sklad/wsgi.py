"""
WSGI-конфигурация для project_sklad.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_sklad.settings')

application = get_wsgi_application()
