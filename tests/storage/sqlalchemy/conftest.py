from acquiring import utils

if utils.is_sqlalchemy_installed():
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
