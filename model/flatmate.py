from pydantic import BaseModel
from datetime import date


class Flatmate(BaseModel):
    username: str
    flat_code: str
    room_id: int
    join_date: date