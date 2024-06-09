from acquiring import utils

# TODO models must be exposed, rather than having to access storage.***.models

if utils.is_django_installed():
    from .django import models

elif utils.is_sqlalchemy_installed():
    from .sqlalchemy import models  # type:ignore[no-redef]

__all__ = ["models"]
