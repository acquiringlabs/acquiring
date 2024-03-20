import pytest
from django_test_migrations.plan import all_migrations, nodes_to_tuples


@pytest.mark.django_db
def test_migrationOrderingIsCorrect():
    main_migrations = all_migrations(
        "default",
        [
            "django_acquiring",
        ],
    )

    assert nodes_to_tuples(main_migrations) == [("django_acquiring", "0001_initial")]
