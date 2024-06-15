import asyncio

from _pytest.fixtures import fixture
from genie_datastores.testing.postgres import PostgresTestkit
from sqlalchemy.ext.asyncio import AsyncEngine


@fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@fixture(scope="session")
def postgres_testkit() -> PostgresTestkit:
    with PostgresTestkit() as testkit:
        yield testkit


@fixture(scope="session")
def postgres_engine(postgres_testkit: PostgresTestkit) -> AsyncEngine:
    return postgres_testkit.get_database_engine()
