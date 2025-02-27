from conftest import TEST_TASKS_CSV
from models import Task, TaskType, TaskWithID
from operations import create_task, modify_task, read_task, read_tasks, remove_task

"""
EXERCISE

Try to write your unit tests for each one of the CRUD operations. If you follow
along with the GitHub repository, you can find the tests in the
Chapter03/task_manager_rest_api/test_operations.py file.
"""


class TestOperations:
    def test_read_tasks(self):
        excepted = [TaskWithID(**task) for task in TEST_TASKS_CSV]
        result = read_tasks()
        assert result == excepted

    def test_read_task(self):
        task_id = 1
        excepted = TaskWithID(**TEST_TASKS_CSV[0])
        result = read_task(task_id)
        assert result == excepted

    def test_create_task(self):
        new_task = Task(
            title="Test Task Three",
            description="Test Description Three",
            status=TaskType.OPEN,
        )
        result = create_task(new_task)

        assert result.id == 3
        assert read_task(3) == TaskWithID(id=3, **new_task.model_dump())

    def test_modify_task(self):
        updated_task = {
            "title": "Updated Test Task One",
        }
        modify_task(1, updated_task)
        assert read_task(1).title == "Updated Test Task One"

    def test_remove_task(self):
        remove_task(1)
        assert read_task(1) is None
