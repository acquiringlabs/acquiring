import pytest
from acquiring.utils import is_django_installed

skip_if_django_not_installed = pytest.mark.skipif(not is_django_installed(), reason="django is not installed")
