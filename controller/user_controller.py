from fastapi import HTTPException

from model import user as us
from dao import user_dao
from fastapi import APIRouter

user_router = APIRouter()


@user_router.post("/user/", response_model=us.User, tags=["user"])
def create_user(user: us.UserWithPassword):
    db_user = user_dao.get_user_by_user_name(username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User name not available")
    return user_dao.create_user(user=user)


@user_router.get("/user_by_email/", response_model=us.User, tags=["user"])
def get_user_by_email_id(email_id: str):

    db_user = user_dao.get_user_by_email(email_id=email_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@user_router.get("/user/", response_model=us.User, tags=["user"])
def get_user_by_username(username: str):

    db_user = user_dao.get_user_by_user_name(username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@user_router.delete("/user/", tags=["user"])
def delete_user_by_username(username: str):

    db_user = user_dao.get_user_by_user_name(username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_dao.delete_user_by_user_name(username=username)
    return {"result": f"User {username} is deleted."}
