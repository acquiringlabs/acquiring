"""Django settings required to test the application"""

# TODO Remove this file once the testing is possible without it.

DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
    "secondary": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
}

INSTALLED_APPS = ("acquiring",)

# TODO Figure out a way to do away with this custom config, which is annoying for users
MIGRATION_MODULES = {"acquiring": "acquiring.storage.django.migrations"}
