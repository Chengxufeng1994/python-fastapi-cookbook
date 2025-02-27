import csv
from typing import Optional

from models import Task, TaskType, TaskV2WithID, TaskWithID

DATABASE_FILENAME = "tasks.csv"
column_fields = list(["id", "title", "description", "status"])


def next_identity() -> int:
    try:
        with open(DATABASE_FILENAME, newline="") as file:
            reader = csv.DictReader(file, delimiter=",")
            max_id = max(int(task["id"]) for task in reader)
            return max_id + 1
    except FileNotFoundError:
        return 1
    except ValueError:
        return 1


def read_tasks() -> list[TaskWithID]:
    with open(DATABASE_FILENAME, newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        return [
            TaskWithID(
                id=int(row["id"]),
                title=row["title"],
                description=row["description"],
                status=TaskType(row["status"]),
            )
            for row in reader
        ]


def read_tasks_v2():
    with open(DATABASE_FILENAME, newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        return [TaskV2WithID(**row) for row in reader]


def read_task(task_id: int) -> TaskWithID | None:
    try:
        with open(DATABASE_FILENAME, newline="") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=",")
            for row in reader:
                if int(row["id"]) == task_id:
                    return TaskWithID(
                        id=int(row["id"]),
                        title=row["title"],
                        description=row["description"],
                        status=TaskType(row["status"]),
                    )

        return None
    except FileNotFoundError:
        return None

    # tasks = read_tasks()
    # for task in tasks:
    #     if task.id == task_id:
    #         return task
    # return None


def write_tasks_into_csv(task: TaskWithID) -> None:
    with open(DATABASE_FILENAME, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=column_fields)
        # covert model to json
        writer.writerow(
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
            }
        )


def create_task(task: Task) -> TaskWithID:
    id = next_identity()
    task_with_id = TaskWithID(
        id=id,
        **task.model_dump(),
    )
    write_tasks_into_csv(task_with_id)
    return task_with_id


def modify_task(id: int, task: dict) -> TaskWithID | None:
    if task["status"] is not None:
        task["status"] = TaskType(task["status"])

    updated_task: Optional[TaskWithID] = None
    tasks = read_tasks()
    for index, task_ in enumerate(tasks):
        if task_.id == id:
            updated_task = task_.model_copy(update=task)  # Override status in task dict
            tasks[index] = updated_task

    with open(DATABASE_FILENAME, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=column_fields)
        writer.writeheader()
        for task_ in tasks:
            print(task_.status.value)
            writer.writerow(
                {
                    "id": task_.id,
                    "title": task_.title,
                    "description": task_.description,
                    "status": task_.status.value,
                }
            )

    if updated_task is not None:
        return updated_task

    return None


def remove_task(id: int) -> Task | None:
    deleted_task: TaskWithID | None = None
    tasks = read_tasks()
    with open(DATABASE_FILENAME, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=column_fields)
        writer.writeheader()
        for task in tasks:
            if task.id == id:
                deleted_task = task
                continue

            writer.writerow(
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status.value,
                }
            )

    if deleted_task:
        deleted_task_without_id = deleted_task.model_dump()
        del deleted_task_without_id["id"]
        return Task(**deleted_task_without_id)

    return None
