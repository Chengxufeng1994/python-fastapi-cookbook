import json
from fastapi.exceptions import HTTPException, RequestValidationError
from starlette.responses import JSONResponse, PlainTextResponse
from ch01.bookstore.router import author_router, book_router

from fastapi import FastAPI, status

app = FastAPI()

app.include_router(book_router)
app.include_router(author_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": "Oops! Something went wrong"},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(
        f"This is a plain text response: \n{json.dumps(exc.errors(), indent=2)}",
        status_code=status.HTTP_400_BAD_REQUEST,
    )


@app.get("/error_endpoint")
async def raise_exception():
    raise HTTPException(status.HTTP_400_BAD_REQUEST)
