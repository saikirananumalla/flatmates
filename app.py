from fastapi import FastAPI, Depends, HTTPException
from decouple import config
from fastapi.security import HTTPBasicCredentials, HTTPBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
import hashlib
from typing import Annotated

from dao import user_dao

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

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 10


# Function to create JWT tokens
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Dependency to get current user
def get_current_user(token: HTTPBasicCredentials = Depends(HTTPBearer())):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")  
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return payload


# Login route to get JWT token
@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # Hash the password using SHA-256
    hashed_password = hashlib.sha256(form_data.password.encode('utf-8')).hexdigest()
    user = user_dao.get(form_data.username)
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


@app.get("/test-protected")
async def some_protected_endpoint(current_user: dict = Depends(get_current_user)):
    return {"message": "This is a protected endpoint", "user": current_user}