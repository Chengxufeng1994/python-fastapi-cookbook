from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .db_connection import get_session
from .models import Role, User
from .operations import create_user
from .response import ResponseCreateUser, UserCreateBody, UserCreateResponse

router = APIRouter()


@router.post(
    "/register/premium-users",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseCreateUser,
    responses={
        status.HTTP_409_CONFLICT: {"description": "The user already exist"},
        status.HTTP_201_CREATED: {"description": "User created"},
    },
)
async def register_premium_user(
    body: UserCreateBody,
    session: Session = Depends(get_session),
) -> dict[str, str | UserCreateResponse]:
    user = create_user(
        session,
        User(**body.model_dump(), role=Role.premium),
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user or email already exist",
        )
    user_response = UserCreateResponse(
        username=user.username,
        email=user.email,
    )
    return {
        "message": "user successfully created",
        "user": user_response,
    }
