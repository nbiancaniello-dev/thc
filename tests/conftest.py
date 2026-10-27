import os
import sys
from collections.abc import AsyncGenerator

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:challenge@localhost:5432/test_postgres",
)
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")

import asyncio
import selectors

import httpx
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from database import Base, get_db
from main import app
from clients.dragon_ball_client import DragonBallClient
from tests.helpers import FAKE_DRAGON_BALL_CHARACTERS

pytest_plugins = ["anyio"]


@pytest.fixture(autouse=True)
def mock_dragon_ball_api(monkeypatch) -> list[str]:
    """Serve fake data for every DragonBallClient so no test reaches the real API.

    Returns the list of request paths received, so tests can assert on them.
    """
    requested_paths: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requested_paths.append(request.url.path)
        try:
            character_id = int(request.url.path.rsplit("/", 1)[-1])
        except ValueError:
            return httpx.Response(400, json={"message": "Bad request"})
        character = FAKE_DRAGON_BALL_CHARACTERS.get(character_id)
        if character is None:
            return httpx.Response(404, json={"message": "Character not found"})
        return httpx.Response(200, json=character)

    mock_transport = httpx.MockTransport(handler)
    original_init = DragonBallClient.__init__

    def init_with_mock_transport(self, *args, **kwargs):
        # A test can still pass its own transport explicitly
        if kwargs.get("transport") is None:
            kwargs["transport"] = mock_transport
        original_init(self, *args, **kwargs)

    monkeypatch.setattr(DragonBallClient, "__init__", init_with_mock_transport)
    return requested_paths


@pytest.fixture(scope="session")
def anyio_backend():
    if sys.platform == "win32":
        def win_loop_factory():
            return asyncio.SelectorEventLoop(selectors.SelectSelector())

        return "asyncio", {"loop_factory": win_loop_factory}

    return "asyncio"


@pytest.fixture(scope="session")
def test_engine():
    engine = create_async_engine(
        os.environ["DATABASE_URL"],
        poolclass=NullPool,
    )
    return engine


@pytest.fixture(scope="session")
async def setup_database(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


@pytest.fixture
async def db_session(
    test_engine,
    setup_database,
) -> AsyncGenerator[AsyncSession]:
    conn = await test_engine.connect()
    trans = await conn.begin()

    test_async_session = async_sessionmaker(
        bind=conn,
        class_=AsyncSession,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    async with test_async_session() as session:
        try:
            yield session
        finally:
            await session.close()
            await trans.rollback()
            await conn.close()


@pytest.fixture
async def client(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient]:

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
