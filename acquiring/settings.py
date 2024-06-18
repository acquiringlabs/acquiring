"""Django settings required to test the application"""

# TODO Remove this file once the testing is possible without it.

# See https://gcollazo.com/optimal-sqlite-settings-for-django/
DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
    "OPTIONS": {
        "init_command": (
            "PRAGMA foreign_keys=ON;"
            "PRAGMA journal_mode = WAL;"
            "PRAGMA synchronous = NORMAL;"
            "PRAGMA busy_timeout = 5000;"
            "PRAGMA temp_store = MEMORY;"
            "PRAGMA mmap_size = 134217728;"
            "PRAGMA journal_size_limit = 67108864;"
            "PRAGMA cache_size = 2000;"
        ),
        "transaction_mode": "IMMEDIATE",
    },
}

INSTALLED_APPS = ("acquiring",)

# TODO Figure out a way to do away with this custom config, which is annoying for users
MIGRATION_MODULES = {"acquiring": "acquiring.storage.django.migrations"}
