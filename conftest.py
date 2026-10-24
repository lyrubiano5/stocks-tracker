import os
from collections.abc import AsyncIterator

import pytest_asyncio
from sqlalchemy import delete, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from models import Base, Stock


TEST_DATABASE = "stocks_test"


def database_urls() -> tuple[URL, URL]:
    database_url = os.environ["DATABASE_URL"]
    base_url = make_url(database_url)
    test_url = base_url.set(database=TEST_DATABASE)
    maintenance_url = base_url.set(database="postgres")

    if test_url.database == base_url.database:
        raise AssertionError("Tests must use stocks_test, not the stocks database")

    return maintenance_url, test_url


async def create_test_database(maintenance_engine: AsyncEngine) -> None:
    async with maintenance_engine.connect() as connection:
        database_exists = await connection.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :database"),
            {"database": TEST_DATABASE},
        )
        if not database_exists:
            await connection.commit()
            autocommit_connection = await connection.execution_options(
                isolation_level="AUTOCOMMIT"
            )
            await autocommit_connection.execute(
                text(f'CREATE DATABASE "{TEST_DATABASE}"')
            )


@pytest_asyncio.fixture
async def session_maker() -> AsyncIterator[async_sessionmaker]:
    maintenance_url, test_url = database_urls()
    maintenance_engine = create_async_engine(maintenance_url)
    await create_test_database(maintenance_engine)
    await maintenance_engine.dispose()

    engine = create_async_engine(test_url)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    maker = async_sessionmaker(engine, expire_on_commit=False)
    yield maker

    await engine.dispose()


@pytest_asyncio.fixture
async def clean_database(session_maker: async_sessionmaker) -> None:
    async with session_maker() as session:
        await session.execute(delete(Stock))
        await session.commit()
