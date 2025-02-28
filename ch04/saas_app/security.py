from datetime import datetime, timedelta
from typing import Optional

from email_validator import EmailNotValidError, validate_email
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .db_connection import get_session
from .models import User, UserInDB
from .operations import get_user_by_email, get_user_by_username

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def authenticate_user(session: Session, user: User) -> Optional[UserInDB]:
    if user is None:
        return None

    existed_user: Optional[UserInDB] = None
    if user.email:
        try:
            validate_email(user.email)
        except EmailNotValidError:
            return None
        existed_user = get_user_by_email(session, user.email)
    elif user.username:
        existed_user = get_user_by_username(session, user.username)

    if not existed_user or not pwd_context.verify(user.password, existed_user.password):
        return None

    return existed_user


SECRET_KEY = "a_very_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str, db_session: Session) -> User | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
    except JWTError:
        return None
    if not username:
        return None
    user = get_user_by_username(db_session, username)
    return user


router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post(
    "/token",
    response_model=Token,
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Incorrect username or password"}},
)
def get_user_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = authenticate_user(
        session,
        User(username=form_data.username, password=form_data.password, email=""),
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get(
    "/users/me",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "User not authorized"},
        status.HTTP_200_OK: {"description": "username authorized"},
    },
)
def read_user_me(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
):
    user = decode_access_token(token, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authorized",
        )
    return {
        "description": f"{user.username} authorized",
    }
