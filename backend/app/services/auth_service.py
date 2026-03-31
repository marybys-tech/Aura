import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.constants import ALL_CATEGORIES
from app.core.exceptions import UnauthorizedError
from app.core.oauth import OAuthUserInfo
from app.core.security import create_access_token, generate_refresh_token, hash_token
from app.models.category_score import CategoryScore
from app.models.user import RefreshToken, User
from app.schemas.auth import TokenResponse


async def upsert_user_from_oauth(db: AsyncSession, info: OAuthUserInfo) -> User:
    """Create user on first login, update avatar/name on subsequent logins."""
    result = await db.execute(
        select(User).where(User.oauth_provider == info.provider, User.oauth_provider_id == info.provider_id)
    )
    user = result.scalar_one_or_none()

    if user:
        user.display_name = info.display_name
        user.avatar_url = info.avatar_url
    else:
        user = User(
            email=info.email,
            display_name=info.display_name,
            avatar_url=info.avatar_url,
            oauth_provider=info.provider,
            oauth_provider_id=info.provider_id,
        )
        db.add(user)
        await db.flush()
        await _init_category_scores(db, user.id)

    await db.commit()
    await db.refresh(user)
    return user


async def _init_category_scores(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Initialize 6 category score rows for a new user with vitality 50."""
    for cat in ALL_CATEGORIES:
        db.add(CategoryScore(
            user_id=user_id,
            category=cat.value,
            level=0,
            xp=0.0,
            xp_to_next=10.0,
            vitality=50.0,
        ))


async def issue_tokens(db: AsyncSession, user: User) -> TokenResponse:
    """Create access + refresh token pair."""
    access_token = create_access_token(user.id)
    raw_refresh = generate_refresh_token()

    rt = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(raw_refresh),
        expires_at=datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(rt)
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=raw_refresh,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


async def refresh_tokens(db: AsyncSession, raw_refresh: str) -> TokenResponse:
    """Rotate refresh token: revoke old, issue new pair."""
    token_hash = hash_token(raw_refresh)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash, RefreshToken.revoked == False)  # noqa: E712
    )
    rt = result.scalar_one_or_none()

    if not rt or rt.expires_at < datetime.now(UTC):
        raise UnauthorizedError("Invalid or expired refresh token")

    rt.revoked = True

    result = await db.execute(select(User).where(User.id == rt.user_id))
    user = result.scalar_one()

    return await issue_tokens(db, user)


async def revoke_refresh_token(db: AsyncSession, raw_refresh: str) -> None:
    """Revoke a specific refresh token (logout)."""
    token_hash = hash_token(raw_refresh)
    result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    rt = result.scalar_one_or_none()
    if rt:
        rt.revoked = True
        await db.commit()
