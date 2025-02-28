import httpx
from fastapi import APIRouter, HTTPException, status

from .security import Token
from .third_party_login import (
    GITHUB_AUTHORIZATION_URL,
    GITHUB_CLIENT_ID,
    GITHUB_CLIENT_SECRET,
    GITHUB_REDIRECT_URI,
)

router = APIRouter()


@router.get("/github/auth/url")
async def github_login():
    auth_url = f"{GITHUB_AUTHORIZATION_URL}" f"?client_id={GITHUB_CLIENT_ID}"
    return {"auth_url": auth_url}


@router.get(
    "/github/auth/token",
    response_model=Token,
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "User not registered"}},
)
async def github_token(code: str):
    github_url = "https://github.com/login/oauth/access_token"
    response = httpx.post(
        github_url,
        data={
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": GITHUB_REDIRECT_URI,
        },
        headers={"Accept": "application/json"},
    ).json()
    access_token = response.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="User not registered",
        )
    token_type = response.get("token_type", "bearer")
    return {
        "access_token": access_token,
        "token_type": token_type,
    }
