from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import User, UserInDB
from .orm_entity import User as UserOrmEntity

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def create_user(session: Session, user: User) -> UserInDB | None:
    hashed_password = pwd_context.hash(user.password)

    user_orm_entity = UserOrmEntity(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
    )
    session.add(user_orm_entity)
    try:
        session.commit()
        session.refresh(user_orm_entity)
    except IntegrityError:
        session.rollback()
        return None

    return UserInDB(
        id=user_orm_entity.id,
        username=user_orm_entity.username,
        email=user_orm_entity.email,
        password=user_orm_entity.hashed_password,
    )


def get_user(session: Session, user_id: int) -> UserInDB | None:
    user_orm_entity = session.query(UserOrmEntity).filter(UserOrmEntity.id == user_id).first()
    if user_orm_entity is None:
        return None
    return UserInDB(
        id=user_orm_entity.id,
        username=user_orm_entity.username,
        email=user_orm_entity.email,
        password=user_orm_entity.hashed_password,
        role=user_orm_entity.role,
        totp_secret=user_orm_entity.totp_secret,
    )

    # # Method 2:
    # stmt = select(User).filter(User.id == user_id)
    # user = session.scalars(stmt).one_or_none()
    # if user is None:
    #     return None
    # return UserInDB(
    #     id=user.id,
    #     username=user.username,
    #     email=user.email,
    #     hashed_password=user.hashed_password,
    # )


def get_user_by_email(session: Session, email: str) -> UserInDB | None:
    user_orm_entity = session.query(UserOrmEntity).filter(UserOrmEntity.email == email).first()
    if user_orm_entity is None:
        return None
    return UserInDB(
        id=user_orm_entity.id,
        username=user_orm_entity.username,
        email=user_orm_entity.email,
        password=user_orm_entity.hashed_password,
        role=user_orm_entity.role,
        totp_secret=user_orm_entity.totp_secret,
    )


def get_user_by_username(session: Session, username: str) -> UserInDB | None:
    user_orm_entity = (
        session.query(UserOrmEntity).filter(UserOrmEntity.username == username).first()
    )
    if user_orm_entity is None:
        return None
    return UserInDB(
        id=user_orm_entity.id,
        username=user_orm_entity.username,
        email=user_orm_entity.email,
        password=user_orm_entity.hashed_password,
        role=user_orm_entity.role,
        totp_secret=user_orm_entity.totp_secret,
    )


def update_user(session: Session, user: UserInDB):
    user_orm_entity = session.query(UserOrmEntity).filter(UserOrmEntity.id == user.id).first()
    if user_orm_entity is None:
        return None
    user_orm_entity.username = user.username
    user_orm_entity.email = user.email
    user_orm_entity.hashed_password = user.password
    user_orm_entity.role = user.role
    if user.totp_secret:
        user_orm_entity.totp_secret = user.totp_secret
    session.commit()
    session.refresh(user_orm_entity)
    return UserInDB(
        id=user_orm_entity.id,
        username=user_orm_entity.username,
        email=user_orm_entity.email,
        password=user_orm_entity.hashed_password,
        role=user_orm_entity.role,
        totp_secret=user_orm_entity.totp_secret,
    )
