from django.apps import AppConfig
from django.db.models.signals import post_migrate

class MyappConfig(AppConfig):
    name = 'myapp'

    def ready(self):
        from .auth_bootstrap import seed_default_admin_on_migrate

        post_migrate.connect(seed_default_admin_on_migrate, sender=self)
