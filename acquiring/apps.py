"""Apps contains a registry of installed applications that stores configuration and provides introspection."""

from django.apps import AppConfig


class AcquiringConfig(AppConfig):
    """Store metadata for the application in Django"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "acquiring"
    verbose_name = "Acquiring"
