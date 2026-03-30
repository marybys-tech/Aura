from dataclasses import dataclass

import httpx

from app.config import settings


@dataclass
class OAuthUserInfo:
    email: str
    display_name: str
    avatar_url: str | None
    provider: str
    provider_id: str


def github_login_url() -> str:
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
        "scope": "read:user user:email",
    }
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    return f"https://github.com/login/oauth/authorize?{qs}"


async def github_callback(code: str) -> OAuthUserInfo:
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "code": code,
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET.get_secret_value(),
                "redirect_uri": settings.GITHUB_REDIRECT_URI,
            },
            headers={"Accept": "application/json"},
        )
        token_resp.raise_for_status()
        access_token = token_resp.json()["access_token"]

        user_resp = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_resp.raise_for_status()
        data = user_resp.json()

        email = data.get("email")
        if not email:
            emails_resp = await client.get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            emails_resp.raise_for_status()
            for e in emails_resp.json():
                if e.get("primary"):
                    email = e["email"]
                    break

    return OAuthUserInfo(
        email=email or f"{data['id']}@github.noemail",
        display_name=data.get("name") or data["login"],
        avatar_url=data.get("avatar_url"),
        provider="github",
        provider_id=str(data["id"]),
    )
