from model import flatmate
from dao import flatmate_dao
from fastapi import APIRouter, HTTPException
from pydantic.schema import List

flatmate_router = APIRouter()

@flatmate_router.post("/flatmate", response_model=flatmate.FlatmateWithRoomName, tags=["flatmate"])
def join_flat(flatmate: flatmate.FlatmateBase):
    try:
        return flatmate_dao.create_flatmate(flatmate)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@flatmate_router.delete("/flatmate/{username}", tags=["flatmate"])
def leave_flat(username: str):
    try:
        success = flatmate_dao.delete_flatmate(username)
        if not success:
            raise HTTPException(status_code=404, detail="flatmate not found")
        return success
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@flatmate_router.put("/flatmate/{username}", response_model=flatmate.FlatmateWithRoomName, tags=["flatmate"])
def update_flatmate_room(username: str, room_name: str):
    try:
        result = flatmate_dao.update_room(username, room_name)
        if result is None:
            raise HTTPException(status_code=404, detail="flatmate not found")

        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@flatmate_router.get("/flatmate/{username}", response_model=flatmate.FlatmateWithRoomName, tags=["flatmate"])
def get_flatmate(username: str):
    try:
        result = flatmate_dao.get_flatmate(username)
        
        if result is None:
            raise HTTPException(status_code=404, detail="flatmate not found")

        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    
    
@flatmate_router.get("/flatmates/{flat_code}", response_model=List[flatmate.FlatmateWithRoomName], tags=["flatmate"])
def get_flatmates_in_flat(flat_code: str):
    try:
        result = flatmate_dao.get_flatmates_by_flat(flat_code)
        if result is None:
            raise HTTPException(status_code=404, detail="flat does not exist")
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))