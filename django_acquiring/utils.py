import importlib.util


def is_django_installed() -> bool:
    return bool(importlib.util.find_spec("django"))
