from model import flat
from dao import flat_dao, flatmate_dao
from fastapi import APIRouter, HTTPException, Depends
from config.oauth import get_current_user
from model import user, flatmate

flat_router = APIRouter()

@flat_router.post("/flat", response_model=flat.Flat, tags=["flat"])
def create_flat(flat_name: str, current_user: user.AuthUser = Depends(get_current_user)):
    try:
        if current_user.flat_code is not None:
            raise HTTPException(status_code=401, detail="Not Authorized, user already registered in a flat")
        
        resp = flat_dao.create_flat(name=flat_name)
        flatmate_dao.create_flatmate(flatmate.FlatmateBase(username=current_user.username, flat_code=current_user.flat_code))
        return resp
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@flat_router.delete("/flat/{flat_code}", tags=["flat"])
def delete_flat(flat_code: str, current_user: user.AuthUser = Depends(get_current_user)):
    try:
        if current_user.flat_code != flat_code:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        success = flat_dao.delete_flat_by_code(flat_code=flat_code)
        if not success:
            raise HTTPException(status_code=404, detail="Flat not found")
        return success
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@flat_router.put("/flat", response_model=flat.Flat, tags=["flat"])
def update_flat(flat_name: str, current_user: user.AuthUser = Depends(get_current_user)):
    try:
        if current_user.flat_code is None:
            raise HTTPException(status_code=401, detail="User not in the flat")
        result = flat_dao.update_flat_name(current_user.flat_code, flat_name)
        if result is None:
            raise HTTPException(status_code=404, detail="Flat not found")

        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@flat_router.get("/flat", response_model=flat.Flat, tags=["flat"])
def get_flat(current_user: user.AuthUser = Depends(get_current_user)):
    try:
        result = flat_dao.get_flat(current_user.flat_code)
        if result is None:
            raise HTTPException(status_code=404, detail="Flat not found")

        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))