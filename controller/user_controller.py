from fastapi import HTTPException, Depends

from config.oauth import get_current_user
from model import user as us, user
from dao import user_dao
from fastapi import APIRouter

user_router = APIRouter()


@user_router.post("/user/", response_model=us.User, tags=["user"])
def create_user(username: us.UserWithPassword):
    try:
        db_user = user_dao.get_user_by_user_name(username=username.username)
        if db_user:
            raise HTTPException(status_code=400, detail="User name not available")
        return user_dao.create_user(user=username)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@user_router.get("/user_by_email/", response_model=us.User, tags=["user"])
def get_user_by_email_id(
    email_id: str, current_user: user.AuthUser = Depends(get_current_user)
):
    try:
        db_user = user_dao.get_user_by_email(email_id=email_id)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if current_user.username != db_user.username:
            raise HTTPException(status_code=401, detail="User not authorised")
        return db_user
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@user_router.get("/user/", response_model=us.User, tags=["user"])
def get_user_by_username(current_user: user.AuthUser = Depends(get_current_user)):
    try:
        db_user = user_dao.get_user_by_user_name(username=current_user.username)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if current_user.username != db_user.username:
            raise HTTPException(status_code=401, detail="User not authorised")
        return db_user
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@user_router.put("/update/profile", response_model=us.User, tags=["user"])
def update_user_profile(
    user_details: user.UpdateProfile,
    current_user: user.AuthUser = Depends(get_current_user),
):
    try:

        db_user = user_dao.get_user_by_user_name(username=current_user.username)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if current_user.username != db_user.username:
            raise HTTPException(status_code=401, detail="User not authorised")
        update_user_profile_result = user_dao.update_user_profile(
            user_details, current_user.username
        )
        return update_user_profile_result

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@user_router.delete("/user/", tags=["user"])
def delete_user_by_username(
    username: str, current_user: user.AuthUser = Depends(get_current_user)
):
    try:
        db_user = user_dao.get_user_by_user_name(username=username)
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if current_user.username != db_user.username:
            raise HTTPException(status_code=401, detail="User not authorised")
        user_dao.delete_user_by_user_name(username=username)
        return {"result": f"User {username} is deleted."}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
