from fastapi import FastAPI

from controller.payment_controller import payment_router
from controller.task_controller import task_router
from controller.user_controller import user_router
from controller.flat_controller import flat_router
from controller.room_controller import room_router
from controller.flatmate_controller import flatmate_router
from controller.belonging_controller import belonging_router

app = FastAPI()
app.include_router(user_router)
app.include_router(payment_router)
app.include_router(flat_router)
app.include_router(room_router)
app.include_router(flatmate_router)
app.include_router(task_router)
