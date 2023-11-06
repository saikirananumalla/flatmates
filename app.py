from fastapi import FastAPI
from config.db import get_connection

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session


from schema import user_schema
from database import user_db
from database.database_config import SessionLocal

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
        print(exec_stmt)
        cur.execute(
            exec_stmt,
            (
                {test_user.get("user_name")},
                {test_user.get("email_id")},
                {test_user.get("phone")},
                {test_user.get("password")},
            ),
        )
        get_connection().commit()
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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=user_schema.User)
def create_user(user: user_schema.User, db: Session = Depends(get_db)):
    db_user = user_db.get_user_by_email(db, email=user.email_id)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_db.create_user(db=db, user=user)


@app.get("/users/{user_name}", response_model=user_schema.User)
def read_user(user_name: str, db: Session = Depends(get_db)):
    db_user = user_db.get_user_by_user_name(db, user_name=user_name)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
