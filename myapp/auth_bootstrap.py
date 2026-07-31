from datetime import date

from django.db import OperationalError, ProgrammingError

from .models import Admin, User


DEFAULT_ADMIN_EMAIL = "admin@example.com"
DEFAULT_ADMIN_PASSWORD = "admin123"


def ensure_default_admin_exists() -> None:
    try:
        user, _ = User.objects.get_or_create(
            email=DEFAULT_ADMIN_EMAIL,
            defaults={
                "password": DEFAULT_ADMIN_PASSWORD,
                "user_type": "admin",
            },
        )
    except (OperationalError, ProgrammingError):
        # Tables may not exist yet during early startup (before migrations).
        return

    updates = {}
    if user.user_type != "admin":
        updates["user_type"] = "admin"
    if user.password != DEFAULT_ADMIN_PASSWORD:
        updates["password"] = DEFAULT_ADMIN_PASSWORD
    if updates:
        User.objects.filter(pk=user.pk).update(**updates)
        user.refresh_from_db()

    Admin.objects.get_or_create(
        user=user,
        defaults={
            "name": "Default",
            "familyname": "Admin",
            "phone": "0000000000",
            "address": "System",
            "hiredate": date.today(),
            "department": "Administration",
        },
    )


def seed_default_admin_on_migrate(**kwargs) -> None:
    ensure_default_admin_exists()
