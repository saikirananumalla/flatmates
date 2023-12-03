from model import flatmate
from dao import flatmate_dao
from fastapi import APIRouter, HTTPException, Depends
from pydantic.schema import List
from config.oauth import get_current_user
from model import user

flatmate_router = APIRouter()

@flatmate_router.post("/flatmate", response_model=flatmate.FlatmateWithRoomName, tags=["flatmate"])
def join_flat(flat_code: str, current_user: user.AuthUser = Depends(get_current_user)):
    try:
        if current_user.flat_code is not None:
            raise HTTPException(status_code=401, detail="User already registered in a flat")
        
        return flatmate_dao.create_flatmate(flatmate.FlatmateBase(username=current_user.username, flat_code=flat_code))
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@flatmate_router.delete("/flatmate/", tags=["flatmate"])
def leave_flat(current_user: user.AuthUser = Depends(get_current_user)):
    try:
        if current_user.flat_code is None:
            raise HTTPException(status_code=401, detail="User not registered in any flat")
        
        success = flatmate_dao.delete_flatmate(current_user.username)
        if not success:
            raise HTTPException(status_code=404, detail="flatmate not found")
        return success
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@flatmate_router.put("/flatmate/", response_model=flatmate.FlatmateWithRoomName, tags=["flatmate"])
def update_flatmate_room(room_name: str, current_user: user.AuthUser = Depends(get_current_user)):
    try:
        
        if current_user.flat_code is None:
            raise HTTPException(status_code=401, detail="User not registered in any flat")
        
        result = flatmate_dao.update_room(current_user.username, room_name)
        if result is None:
            raise HTTPException(status_code=404, detail="flatmate not found")

        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@flatmate_router.get("/flatmate", response_model=flatmate.FlatmateWithRoomName, tags=["flatmate"])
def get_flatmate(current_user: user.AuthUser = Depends(get_current_user)):
    try:
        
        if current_user.flat_code is None:
            raise HTTPException(status_code=401, detail="User not registered in any flat")
        
        result = flatmate_dao.get_flatmate(current_user.username)
        
        if result is None:
            raise HTTPException(status_code=404, detail="flatmate not found")

        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    
    
@flatmate_router.get("/flatmates/flat/all", response_model=List[flatmate.FlatmateWithRoomName], tags=["flatmate"])
def get_flatmates_in_flat(current_user: user.AuthUser = Depends(get_current_user)):
    try:
        
        if current_user.flat_code is None:
            raise HTTPException(status_code=401, detail="User not registered in any flat")
        
        result = flatmate_dao.get_flatmates_by_flat(current_user.flat_code)
        if result is None:
            raise HTTPException(status_code=404, detail="flat does not exist")
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))