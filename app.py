from fastapi import FastAPI
from controller.user_controller import user_router
from controller.flat_controller import flat_router
from controller.room_controller import room_router
from controller.flatmate_controller import flatmate_router

app = FastAPI()
app.include_router(user_router)
app.include_router(flat_router)
app.include_router(room_router)
app.include_router(flatmate_router)

@app.get("/")
async def index(msg: str) -> str:
    return msg