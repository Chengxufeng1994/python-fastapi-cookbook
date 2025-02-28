from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from .db_connection import get_session
from .operations import get_user_by_username
from .rbac import get_current_user
from .response import UserCreateResponse

router = APIRouter()


@router.post("/login")
async def login(
    response: Response,
    user: UserCreateResponse = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    existed_user = get_user_by_username(session, user.username)
    if not existed_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    response.set_cookie(key="fakesession", value=f"{existed_user.id}")
    return {"message": "User logged in successfully"}


@router.post("/logout")
async def logout(
    response: Response,
    user: UserCreateResponse = Depends(get_current_user),
):
    response.delete_cookie("fakesession")  # Clear session data
    return {"message": "User logged out successfully"}
