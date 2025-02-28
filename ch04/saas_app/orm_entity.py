from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import String

from .models import Role

"""
Set up a User class to map the users table in the SQL database.
The table should contain the id, username, email, and hashed_password fields.
Establish the connection between the application and the database.
"""


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )
    username: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column()
    role: Mapped[Role] = mapped_column(
        default=Role.basic,
    )
    totp_secret: Mapped[str] = mapped_column(
        nullable=True,
    )
