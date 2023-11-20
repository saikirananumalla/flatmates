from fastapi import FastAPI

from controller.payment_controller import payment_router
from controller.user_controller import user_router

app = FastAPI()
app.include_router(user_router)
app.include_router(payment_router)


@app.get("/")
async def index() -> str:

    msg = "Hello World "
    return msg
