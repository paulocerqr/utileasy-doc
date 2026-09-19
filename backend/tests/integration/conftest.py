import os
from collections.abc import Generator

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine
from sqlalchemy import create_engine as create_sqlalchemy_engine
from sqlalchemy.orm import Session


@pytest.fixture(scope="session")
def postgres_engine() -> Generator[Engine]:
    database_url = os.getenv("TEST_DATABASE_URL")
    if database_url is None:
        pytest.skip("TEST_DATABASE_URL is required for PostgreSQL integration tests")

    alembic_config = Config("alembic.ini")
    alembic_config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    command.upgrade(alembic_config, "head")

    engine = create_sqlalchemy_engine(database_url)
    yield engine
    engine.dispose()


@pytest.fixture
def database_session(postgres_engine: Engine) -> Generator[Session]:
    connection = postgres_engine.connect()
    transaction = connection.begin()

    with Session(bind=connection, expire_on_commit=False) as session:
        yield session

    transaction.rollback()
    connection.close()
