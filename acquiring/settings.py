"""Django settings required to test the application"""

# TODO Remove this file once the testing is possible without it.

DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
    "secondary": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
}

INSTALLED_APPS = ("acquiring",)

MIGRATION_MODULES = {"acquiring": "acquiring.storage.django.migrations"}
