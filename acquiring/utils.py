"""Set of functions used to control which ORM loads"""

import importlib.util


def is_django_installed() -> bool:
    """True only when django is installed"""
    return bool(importlib.util.find_spec("django"))


def is_sqlalchemy_installed() -> bool:
    """True only when sqlalchemy is installed"""
    return bool(importlib.util.find_spec("sqlalchemy"))
