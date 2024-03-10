from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_acquiring.events"
    verbose_name = "Django Acquiring Events"
