from pydantic import BaseModel, EmailStr
from sqlalchemy import engine, select
from sqlalchemy.orm import Session, query
from starlette import status
from starlette.responses import JSONResponse
from ch02.sql_example.database import SessionLocal, User
from fastapi import APIRouter, Depends, FastAPI, HTTPException


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


user_router = APIRouter()


@user_router.get("/users/")
async def reade_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


# @user_router.get("/users/")
# def read_users():
#     db_gen = get_db()  # 呼叫 get_db() 生成器
#     db = next(db_gen)  # 取得 Session 物件
#     try:
#         users = db.query(User).all()
#         return users
#     finally:
#         next(db_gen, None)  # 確保關閉資料庫連線


class UserCreate(BaseModel):
    name: str
    email: EmailStr


@user_router.post("/users/")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@user_router.get("/users/{user_id}")
async def read_user(user_id: int, db: Session = Depends(get_db)):
    stmt = select(User).filter(User.id == user_id)
    user = db.scalars(stmt).one()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@user_router.put("/users/{user_id}")
async def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    stmt = select(User).filter(
        User.id == user_id,
    )
    exist_user = db.scalars(stmt).one()
    if exist_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    exist_user.name = user.name
    exist_user.email = user.email
    db.commit()
    db.refresh(exist_user)
    return exist_user


@user_router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted"}


app.include_router(user_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )
