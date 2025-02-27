from conftest import TEST_TASKS
from fastapi.testclient import TestClient
from main import app
from operations import read_task, read_tasks

client = TestClient(app)


def test_endpoint_get_tasks():
    response = client.get("/v1/tasks")
    assert response.status_code == 200
    assert response.json() == TEST_TASKS


def test_endpoint_get_task():
    response = client.get("/v1/tasks/1")
    assert response.status_code == 200
    assert response.json() == TEST_TASKS[0]

    response = client.get("/v1/task/5")
    assert response.status_code == 404


def test_endpoint_add_task():
    taskJson = {
        "title": "Test Task One",
        "description": "Test Description One",
        "status": "Ready",
    }
    response = client.post("/tasks", json=taskJson)
    assert response.status_code == 200
    assert response.json() == {"id": 3, **taskJson}
    assert len(read_tasks()) == 3


def test_endpoint_update_task():
    updated_fields = {"status": "Finished"}
    response = client.put("/v1/tasks/2", json=updated_fields)

    assert response.status_code == 200
    assert response.json() == {
        **TEST_TASKS[1],
        **updated_fields,
    }

    response = client.put("/v1/task/3", json=updated_fields)

    assert response.status_code == 404


def test_endpoint_delete_task():
    response = client.delete("/v1/tasks/2")
    assert response.status_code == 200

    expected_response = TEST_TASKS[1]
    del expected_response["id"]

    assert response.json() == expected_response
    assert read_task(2) is None
