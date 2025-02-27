import csv
import os
from pathlib import Path
from unittest.mock import patch

import pytest

TEST_TASK_FIELDS = ["id", "title", "description", "status"]

TEST_DATABASE_FILENAME = "test_tasks.csv"

TEST_TASKS_CSV = [
    {
        "id": "1",
        "title": "Test Task One",
        "description": "Test Description One",
        "status": "Incomplete",
    },
    {
        "id": "2",
        "title": "Test Task Two",
        "description": "Test Description Two",
        "status": "Ongoing",
    },
]

TEST_TASKS = [{**task_json, "id": int(task_json["id"])} for task_json in TEST_TASKS_CSV]


@pytest.fixture(autouse=True)
def create_test_database():
    database_file_location = str(
        Path(__file__).parent / TEST_DATABASE_FILENAME,
    )
    with patch(
        "operations.DATABASE_FILENAME",
        database_file_location,
    ) as mocked_csv:
        with open(
            database_file_location,
            mode="w",
            newline="",
        ) as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=TEST_TASK_FIELDS)
            writer.writeheader()
            writer.writerows(TEST_TASKS_CSV)
            print("")
        yield mocked_csv
        os.remove(database_file_location)
