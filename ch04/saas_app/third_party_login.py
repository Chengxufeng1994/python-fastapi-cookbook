import httpx
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2
from sqlalchemy.orm import Session

from .db_connection import get_session
from .models import UserInDB
from .operations import get_user_by_email, get_user_by_username

GITHUB_CLIENT_ID = "Ov23liCzBTBXujg4YfpB"
GITHUB_CLIENT_SECRET = "33c0398a456ae13a4ba1a2f149fa6b4481775d28"
GITHUB_REDIRECT_URI = "http://localhost:8000/github/auth/token"
GITHUB_AUTHORIZATION_URL = "https://github.com/login/oauth/authorize"


def resolve_github_token(
    token: str = Depends(OAuth2()),
    session: Session = Depends(get_session),
) -> UserInDB:
    user_response = httpx.get(
        "https://api.github.com/user",
        headers={"Authorization": token},
    ).json()
    username = user_response.get("login", " ")
    user = get_user_by_username(session, username)
    if not user:
        email = user_response.get("email", " ")
        user = get_user_by_email(session, email)
    # Process user_response to log
    # the user in or create a new account
    if not user:
        raise HTTPException(status_code=403, detail="Token not valid")
    return user
