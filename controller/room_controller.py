from model import room
from dao import room_dao
from fastapi import APIRouter, HTTPException, Depends
from pydantic.schema import List
from config.oauth import get_current_user
from model import user,room

room_router = APIRouter()

@room_router.post("/room", response_model=room.Room, tags=["room"])
def create_room(room_name: str, current_user: user.AuthUser = Depends(get_current_user)):
    try:
        if current_user.flat_code is None:
            raise HTTPException(status_code=401, detail="User not registered in any flat")
        
        room1 = room.RoomWithoutId(name=room_name, flat_code = current_user.flat_code)
        return room_dao.create_room(room1)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@room_router.delete("/room/{room_id}", tags=["room"])
def delete_room(room_id: str, current_user: user.AuthUser = Depends(get_current_user)):
    try:
        if current_user.flat_code is None:
            raise HTTPException(status_code=401, detail="User not registered in any flat")
        
        success = room_dao.delete_room(room_id, current_user.flat_code)
        if not success:
            raise HTTPException(status_code=404, detail="Room not found")
        return success
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@room_router.put("/room/{room_id}", response_model=room.Room, tags=["room"])
def update_room_by_id(room_id: int, name: str, current_user: user.AuthUser = Depends(get_current_user)):
    try:
        if current_user.flat_code is None:
            raise HTTPException(status_code=401, detail="User not registered in any flat")
        
        result = room_dao.update_room_name(room_id, name, current_user.flat_code)
        if result is None:
            raise HTTPException(status_code=404, detail="Room not found")

        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@room_router.get("/room", response_model=room.Room, tags=["room"])
def get_room(name: str, current_user: user.AuthUser = Depends(get_current_user)):
    try:
        if current_user.flat_code is None:
            raise HTTPException(status_code=401, detail="User not registered in any flat")
        
        result = room_dao.get_room(name, current_user.flat_code)
        if result is None:
            raise HTTPException(status_code=404, detail="Room not found")

        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    
    
@room_router.get("/room/flat/all", response_model=List[room.Room], tags=["room"])
def get_rooms_in_flat(current_user: user.AuthUser = Depends(get_current_user)):
    try:
        if current_user.flat_code is None:
            raise HTTPException(status_code=401, detail="User not registered in any flat")
        
        result = room_dao.get_rooms_by_flat(current_user.flat_code)
        if result is None:
            return []
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))