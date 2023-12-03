from fastapi import FastAPI, Depends, HTTPException
from decouple import config
from fastapi.security import HTTPBasicCredentials, HTTPBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
import hashlib
from typing import Annotated
from config.oauth import create_access_token, get_current_user

from dao import user_dao, flatmate_dao
from model import user

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
app.include_router(belonging_router)


# Login route to get JWT token
@app.post("/login", tags=["login"])
async def login(login_form: user.LoginForm):
    # Hash the password using SHA-256
    hashed_password = hashlib.sha256(login_form.password.encode('utf-8')).hexdigest()
    user = user_dao.get(login_form.username)
    if user is None or hashed_password != user.password:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create and return JWT token
    token_data = {"sub": user.username}
    access_token =  {"access_token": create_access_token(token_data), "token_type": "bearer"}
    return access_token
