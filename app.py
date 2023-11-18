from pydantic.schema import List

from config.db import get_connection

from fastapi import FastAPI, HTTPException


from schema import user_schema
from database import user_db

app = FastAPI()


@app.get("/")
async def index() -> str:

    msg = "Hello World "
    try:

        test_user = {
            "user_name": "some_name_1",
            "email_id": "some_email_1",
            "phone": "phone",
            "password": "some_password_1",
        }
        cur = get_connection().cursor()
        # Use text() to explicitly declare the SQL query
        exec_stmt = (
            "INSERT INTO `user` (`username`, `email_id`, `phone`, `password`) VALUES"
            " (%s, %s, %s, %s)"
        )
        cur.execute("SELECT * FROM user")
        result = cur.fetchall()
        print(result)
        # Check the result to verify if the query was successful
        if cur.rowcount == 1:

            msg += " Worked!"
        else:
            msg += " Didn't Work"
    except Exception as e:

        msg += "Didn't Work" + str(e)
    return msg


@app.post("/user/", response_model=user_schema.User)
def create_user(user: user_schema.User):
    db_user = user_db.get_user_by_user_name(user_name=user.user_name)
    if db_user:
        raise HTTPException(status_code=400, detail="User name already registered")
    return user_db.create_user(user=user)


@app.get("/user_by_email/", response_model=List[user_schema.User])
def read_users_by_email_id(email_id: str):

    db_user = user_db.get_users_by_email(email_id=email_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/user/", response_model=user_schema.User)
def read_users_by_username(username: str):

    db_user = user_db.get_user_by_user_name(user_name=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# delete
@app.delete("/user/")
def delete_user_by_username(username: str):

    db_user = user_db.get_user_by_user_name(user_name=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_db.delete_user_by_user_name(user_name=username)
    return {"result": f"User {username} has been deleted."}
