from acquiring import utils


if utils.is_django_installed():
    from . import django

    __all__ = ["django"]

elif utils.is_sqlalchemy_installed():
    from . import sqlalchemy

    __all__ = ["sqlalchemy"]
