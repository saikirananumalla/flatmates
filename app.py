from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def index() -> str:

    msg = "Hello World "
    return msg
