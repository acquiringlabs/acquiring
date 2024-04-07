from acquiring.utils import is_django_installed


if is_django_installed():
    from . import django as django

    __all__ = ["django"]

    assert __all__ == sorted(__all__), sorted(__all__)
