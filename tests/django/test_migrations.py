import pytest

from acquiring.utils import is_django_installed
from tests.django.utils import skip_if_django_not_installed

if is_django_installed():
    from django_test_migrations.plan import all_migrations, nodes_to_tuples


@skip_if_django_not_installed
@pytest.mark.django_db
def test_migrationOrderingIsCorrect() -> None:
    main_migrations = all_migrations(
        "default",
        [
            "acquiring",
        ],
    )

    assert nodes_to_tuples(main_migrations) == [("acquiring", "0001_initial")]
