"""Decorators to conditionally run tests depending on which ORM loads"""

import pytest

from acquiring import utils

skip_if_django_not_installed = pytest.mark.skipif(not utils.is_django_installed(), reason="django is not installed")
skip_if_sqlalchemy_not_installed = pytest.mark.skipif(
    not utils.is_sqlalchemy_installed(), reason="sqlalchemy is not installed"
)
