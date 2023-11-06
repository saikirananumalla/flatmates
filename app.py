from fastapi import Depends, FastAPI
from config.db import getConnection
from sqlalchemy import text

app = FastAPI()

@app.get("/")
def index() -> str:
    msg = "Hello World "
    try:
        cur = getConnection().cursor()
        # Use text() to explicitly declare the SQL query
        cur.execute("SELECT 1")
        
        # Check the result to verify if the query was successful
        if cur.rowcount == 1:
            msg += " Worked!"
        else:
            msg += " Didn't Work"
    except Exception as e:
        msg += "Didn't Work" + str(e)
    return msg