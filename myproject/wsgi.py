"""
WSGI config for myproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

application = get_wsgi_application()

# Auto-run database migrations on server startup to guarantee database tables exist on cloud containers
try:
    call_command('migrate', interactive=False)
    from myapp.auth_bootstrap import ensure_default_admin_exists
    ensure_default_admin_exists()
except Exception as e:
    import logging
    logging.getLogger(__name__).error(f"Auto-migration/bootstrap error on startup: {e}")

