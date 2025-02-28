from fastapi import status
from fastapi.testclient import TestClient


def test_endpoint_add_basic_user(client: TestClient):
    response = client.post(
        "/register/users",
        json={
            "username": "sheldonsonny",
            "email": "sheldonsonny@email.com",
            "password": "difficultpassword",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["message"] == "user successfully created"
    assert response.json()["user"]["username"] == "sheldonsonny"
    assert response.json()["user"]["email"] == "sheldonsonny@email.com"
