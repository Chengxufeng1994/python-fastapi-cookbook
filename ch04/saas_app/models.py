from enum import Enum

from pydantic import BaseModel


class Role(str, Enum):
    basic = "basic"
    premium = "premium"


class User(BaseModel):
    username: str
    password: str
    email: str
    role: Role = Role.basic
    totp_secret: str | None = None


class UserInDB(User):
    id: int
