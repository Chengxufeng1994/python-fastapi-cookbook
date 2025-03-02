import logging
from hashlib import sha1

from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger("uvicorn")


class HashBodyContentMiddleWare:
    def __init__(self, app: ASGIApp, allowed_paths: list[str]) -> None:
        self.app = app
        self.allowed_paths = allowed_paths

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http" or scope["path"] not in self.allowed_paths:
            await self.app(scope, receive, send)
            return

        async def receive_with_new_body() -> Message:
            message = await receive()
            assert message["type"] == "http.request"

            body = message.get("body", b"")
            message["body"] = f'"{sha1(body).hexdigest()}"'.encode()

            return message

        await self.app(
            scope,
            receive_with_new_body,
            send,
        )
