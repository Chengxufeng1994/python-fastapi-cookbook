from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models import Task, TaskType, TaskV2WithID, TaskWithID, User, UserInDB
from operations import (
    create_task,
    modify_task,
    read_task,
    read_tasks,
    read_tasks_v2,
    remove_task,
)
from pydantic import BaseModel
from security import fake_token_generator, fake_users_db, fakely_hash_password
from starlette import status

app = FastAPI(
    title="Task Manager API",
    description="A simple API to manage tasks",
    version="0.1.0",
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Customized Title",
        version="2.0.0",
        description="This is a custom OpenAPI schema",
        routes=app.routes,
    )
    # del openapi_schema["paths"]["/token"]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore


tasks_router_v1 = APIRouter()
tasks_router_v2 = APIRouter()


@tasks_router_v1.get("/", response_model=list[TaskWithID])
async def get_tasks(status: str | None = None, title: str | None = None):
    tasks = read_tasks()
    if status:
        tasks = [task for task in tasks if task.status.value == status]
    if title:
        tasks = [task for task in tasks if task.title == title]
    return tasks


@tasks_router_v1.get("/search")
async def search_tasks(keyword: str | None = None):
    tasks = read_tasks()
    if not keyword:
        return tasks

    # fuzzy search
    # filtered_tasks = [
    #     task
    #     for task in tasks
    #     if keyword.lower() in task.title.lower() or keyword in task.description.lower()
    # ]

    filtered_tasks = [
        task for task in tasks if keyword.lower() in (task.title + task.description).lower()
    ]
    return filtered_tasks


@tasks_router_v1.get("/{task_id}")
async def get_task(task_id: int):
    task = read_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="task not found")

    return task


class CreateTask(BaseModel):
    title: str
    description: str
    status: str


@tasks_router_v1.post("/", response_model=TaskWithID)
async def add_task(request_body: CreateTask):
    task = Task(
        title=request_body.title,
        description=request_body.description,
        status=TaskType(request_body.status),
    )
    return create_task(task)


class UpdateTask(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None


@tasks_router_v1.put("/{task_id}", response_model=TaskWithID)
async def update_task(task_id: int, task_update: UpdateTask):
    updated = modify_task(task_id, task_update.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="task not found")

    return updated


@tasks_router_v1.delete("/{task_id}", response_model=Task)
async def delete_task(task_id: int):
    deleted = remove_task(task_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="task not found")

    return deleted


@tasks_router_v2.get("/", response_model=list[TaskV2WithID])
async def get_tasks_v2():
    tasks = read_tasks_v2()
    return tasks


async def get_user_from_token(token: Annotated[str, Depends(oauth2_scheme)]) -> UserInDB:
    return UserInDB(username=token, hashed_password=token)


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password
    user_json = fake_users_db.get(username)
    if not user_json:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
        )

    user = UserInDB(**user_json)
    if not fakely_hash_password(password) == user.hashed_password:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
        )

    token = fake_token_generator(user)

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@app.get("/user/me")
async def read_users_me(current_user: Annotated[User, Depends(get_user_from_token)]):
    return current_user


app.include_router(tasks_router_v1, prefix="/v1/tasks", tags=["tasks"])
app.include_router(tasks_router_v2, prefix="/v2/tasks", tags=["tasks"])
