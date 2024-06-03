"""Apps contains a registry of installed applications that stores configuration and provides introspection."""

from importlib import import_module

from django.apps import AppConfig
from django.utils.module_loading import module_has_submodule

ACQUIRNG_MODELS_MODULE_NAME = "storage.django.models"


class AcquiringConfig(AppConfig):
    """Store metadata for the application in Django"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "acquiring"
    verbose_name = "Acquiring"

    def import_models(self) -> None:
        """
        Overrides Django's default model import to search for the models inside the storage folder

        See https://github.com/django/django/blob/main/django/apps/config.py#L262
        """

        # Dictionary of models for this app, primarily maintained in the
        # 'all_models' attribute of the Apps this AppConfig is attached to.
        self.models = self.apps.all_models[self.label]

        if module_has_submodule(self.module, ACQUIRNG_MODELS_MODULE_NAME):
            models_module_name = "%s.%s" % (self.name, ACQUIRNG_MODELS_MODULE_NAME)
            self.models_module = import_module(models_module_name)
