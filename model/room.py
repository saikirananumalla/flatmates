from pydantic import BaseModel

class Room(BaseModel):
    name: str
    flat_code: str
    