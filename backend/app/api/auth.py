from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.oauth import github_callback, github_login_url
from app.database import get_db
from app.schemas.auth import RefreshRequest, TokenResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/github/login", summary="Redirect to GitHub OAuth")
async def github_login():
    return RedirectResponse(github_login_url())


@router.get("/github/callback", response_model=TokenResponse, summary="Handle GitHub OAuth callback")
async def github_oauth_callback(code: str = Query(...), db: AsyncSession = Depends(get_db)):
    info = await github_callback(code)
    user = await auth_service.upsert_user_from_oauth(db, info)
    return await auth_service.issue_tokens(db, user)


@router.post("/refresh", response_model=TokenResponse, summary="Refresh access token")
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.refresh_tokens(db, body.refresh_token)


@router.post("/logout", summary="Revoke refresh token")
async def logout(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    await auth_service.revoke_refresh_token(db, body.refresh_token)
    return {"status": "ok"}
