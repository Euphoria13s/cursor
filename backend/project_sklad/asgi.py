"""
ASGI-конфигурация для project_sklad.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_sklad.settings')

application = get_asgi_application()
