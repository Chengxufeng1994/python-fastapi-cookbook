from typing import Annotated

from pydantic import BaseModel, EmailStr, Field


class UserCreateBody(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserCreateResponse(BaseModel):
    username: str
    email: EmailStr


class ResponseCreateUser(BaseModel):
    message: Annotated[
        str,
        Field(default="user successfully created", example="user successfully created"),
    ]
    user: UserCreateResponse
