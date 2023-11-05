from fastapi import Depends, FastAPI
from config.db import SessionLocal
from sqlalchemy import text

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def index(db: SessionLocal = Depends(get_db)) -> str:
    msg = "Hello World "
    try:
        # Use text() to explicitly declare the SQL query
        result = db.execute(text("SELECT 1"))
        
        # Check the result to verify if the query was successful
        if result.scalar() == 1:
            msg += " Worked!"
        else:
            msg += " Didn't Work"
    except Exception as e:
        msg += "Didn't Work" + str(e)
    return msg