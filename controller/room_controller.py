from model import room
from dao import room_dao
from fastapi import APIRouter, HTTPException
from pydantic.schema import List

room_router = APIRouter()

@room_router.post("/room", response_model=room.Room, tags=["room"])
def create_room(room: room.RoomWithoutId):
    try:
        return room_dao.create_room(room)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@room_router.delete("/room/{room_id}", tags=["room"])
def delete_room(room_id: str):
    try:
        success = room_dao.delete_room(room_id)
        if not success:
            raise HTTPException(status_code=404, detail="Room not found")
        return success
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@room_router.put("/room/{room_id}", response_model=room.Room, tags=["room"])
def update_room_by_id(room_id: int, name: str):
    try:
        result = room_dao.update_room_name(room_id, name)
        if result is None:
            raise HTTPException(status_code=404, detail="Room not found")

        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@room_router.get("/room", response_model=room.Room, tags=["room"])
def get_room(name: str, flat_code: str):
    try:
        result = room_dao.get_room(name, flat_code)
        if result is None:
            raise HTTPException(status_code=404, detail="Room not found")

        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    
    
@room_router.get("/room/{flat_code}", response_model=List[room.Room], tags=["room"])
def get_rooms_in_flat(flat_code: str):
    try:
        result = room_dao.get_rooms_by_flat(flat_code)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))