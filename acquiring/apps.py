"""Apps contains a registry of installed applications that stores configuration and provides introspection."""

from django.apps import AppConfig


class AcquiringConfig(AppConfig):
    """Store metadata for the application in Django"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "acquiring"
    verbose_name = "Acquiring"

    def ready(self) -> None:
        """
        This imports models from acquiring/storage
        instead of having the import on acquiring/models.py,
        which can be now safely removed
        """
        import acquiring.storage.django.models  # noqa: F401
