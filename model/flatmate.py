from pydantic import BaseModel
from datetime import date
from typing import Optional

class FlatmateBase(BaseModel):
    username: str
    flat_code: str

class Flatmate(FlatmateBase):
    room_id: int
    join_date: date
    
class FlatmateWithRoomName(FlatmateBase):
    
    room_name: Optional[str]
    join_date: date