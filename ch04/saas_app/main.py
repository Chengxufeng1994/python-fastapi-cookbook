import sys
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, status
from loguru import logger

from . import api_key, basic_access, github_login, mfa, premium_access, rbac, security, user_sess
from .db_connection import get_engine
from .models import UserInDB
from .orm_entity import Base
from .third_party_login import resolve_github_token

# 設置日誌格式與輸出
logger.remove()  # 移除預設 handler
logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")
logger.add("app.log", rotation="10 MB", level="DEBUG")  # 文件輸出，達到 10MB rotate


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up")
    Base.metadata.create_all(bind=get_engine())
    yield
    logger.info("Shutting down")


app = FastAPI(title="Saas application", lifespan=lifespan)


app.include_router(basic_access.router)
app.include_router(security.router)
app.include_router(premium_access.router)
app.include_router(rbac.router)
app.include_router(github_login.router)
app.include_router(mfa.router)
app.include_router(api_key.router)
app.include_router(user_sess.router)


@app.get(
    "/home",
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "token not valid",
        },
    },
)
def homepage(user: UserInDB = Depends(resolve_github_token)) -> dict[str, str]:
    return {"message": f"logged in {user.username} !"}
