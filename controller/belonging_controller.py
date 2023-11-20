from model import belonging
from dao import belonging_dao
from fastapi import APIRouter, HTTPException
from pydantic.schema import List

belonging_router = APIRouter()

@belonging_router.post("/belonging", response_model=belonging.BelongingStr, tags=["belonging"])
def create_belonging(belonging: belonging.Belonging):
    try:
        return belonging_dao.create_belonging(belonging)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@belonging_router.delete("/belonging/{belonging_id}", tags=["belonging"])
def delete_belonging(belonging_id: int):
    try:
        success = belonging_dao.delete_belonging(belonging_id)
        if not success:
            raise HTTPException(status_code=404, detail="belonging not found")
        return success
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@belonging_router.put("/belonging/{belonging_id}", response_model=belonging.BelongingStr, tags=["belonging"])
def update_belonging(belonging_id: int, belonging: belonging.UpdateBelonging):
    try:
        result = belonging_dao.update_belonging(belonging_id, belonging)
        if result is None:
            raise HTTPException(status_code=404, detail="belonging not found")

        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@belonging_router.get("/belonging", response_model=belonging.BelongingStr, tags=["belonging"])
def get_belonging(name: str, flat_code: str):
    try:
        result = belonging_dao.get_belonging(name, flat_code)
        
        if result is None:
            raise HTTPException(status_code=404, detail="belonging not found")

        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    
    
@belonging_router.get("/belongings/{flat_code}", response_model=List[belonging.BelongingStr], tags=["belonging"])
def get_belongings_in_flat(flat_code: str):
    try:
        result = belonging_dao.get_belongings_by_flat(flat_code)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))