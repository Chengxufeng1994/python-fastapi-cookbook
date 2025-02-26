from fastapi import FastAPI

import router_example

app = FastAPI()
app.include_router(router_example.router)


@app.get("/")
async def read_root():
    return {"Hello": "World"}