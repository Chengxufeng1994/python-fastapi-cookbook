from sqlalchemy.orm import Session

from .models import User, UserInDB
from .operations import create_user
from .orm_entity import User as UserOrmEntity


def test_create_user(session: Session):
    user = create_user(
        session,
        User(
            username="sheldonsonny",
            email="sheldonsonny@email.com",
            password="difficultpassword",
        ),
    )
    assert user is not None
    user_orm_entity = session.query(UserOrmEntity).filter(UserOrmEntity.id == user.id).first()
    assert user_orm_entity is not None
    expected = UserInDB(
        id=user_orm_entity.id,
        username=user_orm_entity.username,
        email=user_orm_entity.email,
        password=user_orm_entity.hashed_password,
    )
    assert user == expected
