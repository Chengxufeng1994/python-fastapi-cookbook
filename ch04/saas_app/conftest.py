import pytest
from fastapi.testclient import TestClient
from passlib.context import CryptContext
from sqlalchemy import QueuePool, create_engine
from sqlalchemy.orm import sessionmaker

from .db_connection import get_session
from .main import app
from .orm_entity import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=QueuePool,
    )

    return engine


@pytest.fixture
def session():
    # Create an in-memory SQLite database
    engine = get_engine()

    Session = sessionmaker(bind=engine)

    # Optionally, create tables in the database
    Base.metadata.create_all(engine)

    # Provide the session object for the test
    session = Session()

    # Yield the session so it can be used in tests
    yield session

    # Optionally, drop the tables if needed
    Base.metadata.drop_all(engine)

    # Clean up: close the session after test
    session.close()


@pytest.fixture
def client(session):
    app.dependency_overrides |= {get_session: lambda: session}
    testclient = TestClient(app)
    return testclient
