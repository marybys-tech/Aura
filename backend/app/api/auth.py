import logging
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings

logger = logging.getLogger(__name__)
from app.core.oauth import github_callback, github_login_url
from app.database import get_db
from app.schemas.auth import RefreshRequest, TokenResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/github/login", summary="Redirect to GitHub OAuth")
async def github_login():
    return RedirectResponse(github_login_url())


@router.get("/github/callback", summary="Handle GitHub OAuth callback")
async def github_oauth_callback(code: str = Query(...), db: AsyncSession = Depends(get_db)):
    """Exchange code for tokens, then redirect to frontend with tokens in query string."""
    try:
        info = await github_callback(code)
        user = await auth_service.upsert_user_from_oauth(db, info)
        tokens = await auth_service.issue_tokens(db, user)
        params = urlencode({
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
        })
        return RedirectResponse(f"{settings.FRONTEND_URL}/oauth/github/callback?{params}")
    except Exception as e:
        logger.exception("GitHub OAuth callback failed: %s", e)
        return RedirectResponse(f"{settings.FRONTEND_URL}/login?error=auth_failed")


@router.post("/refresh", response_model=TokenResponse, summary="Refresh access token")
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.refresh_tokens(db, body.refresh_token)


@router.post("/logout", summary="Revoke refresh token")
async def logout(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    await auth_service.revoke_refresh_token(db, body.refresh_token)
    return {"status": "ok"}
