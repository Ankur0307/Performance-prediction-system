"""
Vercel serverless entry point for the Django application.
Vercel's Python runtime calls the `app` variable as a WSGI handler.
"""
import os
import sys

# Make sure the project root is on the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Tell Django which settings module to use
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

from django.core.wsgi import get_wsgi_application  # noqa: E402

app = get_wsgi_application()
