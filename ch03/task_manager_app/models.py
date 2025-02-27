from enum import Enum

from pydantic import BaseModel


class TaskType(Enum):
    OPEN = "Open"
    READY = "Ready"
    ONGOING = "Ongoing"
    INCOMPLETE = "Incomplete"
    FINISHED = "Finished"


class Task(BaseModel):
    title: str
    description: str
    status: TaskType


class TaskWithID(Task):
    id: int


class TaskV2(BaseModel):
    title: str
    description: str
    status: TaskType
    priority: str | None = "lower"


class TaskV2WithID(TaskV2):
    id: int


class User(BaseModel):
    username: str


class UserInDB(User):
    hashed_password: str
