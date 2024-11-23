"""
WSGI config for booksbuddy_backend project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'booksbuddy_backend.settings')

application = get_wsgi_application()

# Add this for Vercel
app = application