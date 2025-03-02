import logging

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.websockets import WebSocket, WebSocketDisconnect

from .templating import templates
from .ws_manager import ConnectionManager

logger = logging.getLogger("uvicorn")

router = APIRouter()

conn_manager = ConnectionManager()


@router.websocket("/chatroom/{username}")
async def chatroom_endpoint(websocket: WebSocket, username: str):
    await conn_manager.connect(websocket)
    await conn_manager.broadcast(
        {
            "sender": "system",
            "message": f"{username} joined the chat",
        },
        exclude=websocket,
    )

    logger.info(f"{username} joined the chat")
    try:
        while True:
            data = await websocket.receive_text()
            await conn_manager.broadcast(
                {
                    "sender": username,
                    "message": data,
                },
                exclude=websocket,
            )
            await conn_manager.send_personal_message(
                {
                    "sender": "You",
                    "message": data,
                },
                websocket,
            )
    except WebSocketDisconnect:
        conn_manager.disconnect(websocket)
        await conn_manager.broadcast(
            {
                "sender": "system",
                "message": f"{username} " "left the chat",
            }
        )
        logger.info(f"{username} left the chat")


@router.get("/chatroom/{username}")
async def chatroom_page_endpoint(request: Request, username: str) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="chatroom.html",
        context={"username": username},
    )
