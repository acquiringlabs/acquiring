from acquiring import utils

if utils.is_sqlalchemy_installed():
    import contextlib
    from typing import Callable, Generator

    import alembic
    import pytest
    import sqlalchemy
    from alembic.config import Config
    from sqlalchemy import orm

    @pytest.fixture
    def session() -> orm.Session:
        ALEMBIC_CONFIGURATION = Config("alembic.ini")
        try:
            # Set up SQLAlchemy session
            engine = sqlalchemy.create_engine("sqlite:///./db.sqlite3")
            Session = orm.sessionmaker(bind=engine)
            session = Session()

            # Run migrations using Alembic
            alembic.command.upgrade(ALEMBIC_CONFIGURATION, "head")

            # Check that there are tables in the test database
            assert len(session.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()) > 0

            # Pass the session to the tests
            yield session
        finally:
            # Revert migrations
            alembic.command.downgrade(ALEMBIC_CONFIGURATION, "base")

            # Tear session down
            # TODO Figure out what's going on here
            if hasattr(session, "teardown"):  # Normally, this path is the one taken
                session.teardown()
            else:
                # When Ctrl + D, session somehow does not have attr teardown
                session.close()

    @pytest.fixture
    def sqlalchemy_assert_num_queries() -> Callable:
        """TODO implement django_assert_num_queries functionality for sqlalchemy

        It must be some version of this:

        from sqlalchemy.testing import assertions
        with assertions.AssertsExecutionResults.assert_execution(
        assertions.assertsql.CountStatements(count=1),
        db=session,
        )

        For now, it is an empty context manager that can be place where we want
        to eventually check for the number of queries.
        """

        @contextlib.contextmanager
        def context(num: int) -> Generator:
            yield

        return context
