from model import flat
from dao import flat_dao
from fastapi import APIRouter, HTTPException, Depends
from config.oauth import get_current_user
from model import user

flat_router = APIRouter()

@flat_router.post("/flat", response_model=flat.Flat, tags=["flat"])
def create_flat(flat_name: str, current_user: user.AuthUser = Depends(get_current_user)):
    try:
        return flat_dao.create_flat(name=flat_name)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@flat_router.delete("/flat/{flat_code}", tags=["flat"])
def delete_flat(flat_code: str):
    try:
        success = flat_dao.delete_flat_by_code(flat_code=flat_code)
        if not success:
            raise HTTPException(status_code=404, detail="Flat not found")
        return success
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@flat_router.put("/flat/{flat_code}", response_model=flat.Flat, tags=["flat"])
def update_flat(flat: flat.Flat):
    try:
        result = flat_dao.update_flat_name(flat=flat)
        if result is None:
            raise HTTPException(status_code=404, detail="Flat not found")

        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@flat_router.get("/flat/{flat_code}", response_model=flat.Flat, tags=["flat"])
def get_flat(flat_code: str):
    try:
        result = flat_dao.get_flat(flat_code)
        if result is None:
            raise HTTPException(status_code=404, detail="Flat not found")

        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))