from fastapi import FastAPI
from controller.user_controller import user_router
from controller.flat_controller import flat_router

app = FastAPI()
app.include_router(user_router)
app.include_router(flat_router)


@app.get("/")
async def index() -> str:

    msg = "Hello World "
    return msg
