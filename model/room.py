from pydantic import BaseModel

class Room(BaseModel):
    room_id: int
    name: str
    flat_code: str
    
class RoomWithoutId(BaseModel):
    name: str
    flat_code: str
    