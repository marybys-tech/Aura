import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.core.constants import ALL_CATEGORIES
from app.core.security import create_access_token
from app.database import Base, get_db
from app.main import app
from app.models.category_score import CategoryScore
from app.models.user import User

# Use a test database — append _test to the DB name
TEST_DB_URL = settings.DATABASE_URL.replace("/aura", "/aura_test")

engine = create_async_engine(TEST_DB_URL, echo=False)
TestSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def setup_db():
    """Create all tables once per session."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(loop_scope="session")
async def db_session(setup_db) -> AsyncGenerator[AsyncSession, None]:
    """Per-test session with rollback."""
    async with TestSession() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(loop_scope="session")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """ASGI test client with DB override."""

    async def _override_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(loop_scope="session")
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user with category scores."""
    user = User(
        email=f"test-{uuid.uuid4().hex[:8]}@example.com",
        display_name="Test User",
        oauth_provider="github",
        oauth_provider_id=uuid.uuid4().hex,
    )
    db_session.add(user)
    await db_session.flush()

    for cat in ALL_CATEGORIES:
        db_session.add(CategoryScore(user_id=user.id, category=cat.value, score=50.0))
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(loop_scope="session")
async def auth_client(client: AsyncClient, test_user: User) -> AsyncClient:
    """Client with valid auth header."""
    token = create_access_token(test_user.id)
    client.headers["Authorization"] = f"Bearer {token}"
    return client
