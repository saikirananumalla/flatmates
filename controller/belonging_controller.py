from model import belonging
from dao import belonging_dao
from fastapi import APIRouter, HTTPException, Depends
from pydantic.schema import List
from config.oauth import get_current_user
from model import user

belonging_router = APIRouter()

@belonging_router.post("/belonging", response_model=belonging.BelongingStr, tags=["belonging"])
def create_belonging(bg: belonging.UpdateBelonging, current_user: user.AuthUser = Depends(get_current_user)):
    try:
        
        if current_user.flat_code is None:
            raise HTTPException(status_code=401, detail="User not registered in any flat")
        
        belong = belonging.Belonging(description=bg.description, name=bg.name, owners=bg.owners, flat_code= current_user.flat_code)
        return belonging_dao.create_belonging(belong)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@belonging_router.delete("/belonging/{belonging_id}", tags=["belonging"])
def delete_belonging(belonging_id: int, current_user: user.AuthUser = Depends(get_current_user)):
    try:
        
        if current_user.flat_code is None:
            raise HTTPException(status_code=401, detail="User not registered in any flat")
        
        success = belonging_dao.delete_belonging(belonging_id, current_user.flat_code)
        if not success:
            raise HTTPException(status_code=404, detail="belonging not found")
        return success
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@belonging_router.put("/belonging/{belonging_id}", response_model=belonging.BelongingStr, tags=["belonging"])
def update_belonging(belonging_id: int, belonging: belonging.UpdateBelonging, current_user: user.AuthUser = Depends(get_current_user)):
    try:
        
        if current_user.flat_code is None:
            raise HTTPException(status_code=401, detail="User not registered in any flat")
        
        result = belonging_dao.update_belonging(belonging_id, belonging, current_user.flat_code)
        if result is None:
            raise HTTPException(status_code=404, detail="belonging not found")

        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@belonging_router.get("/belonging", response_model=belonging.BelongingStr, tags=["belonging"])
def get_belonging(name: str, current_user: user.AuthUser = Depends(get_current_user)):
    try:
        
        if current_user.flat_code is None:
            raise HTTPException(status_code=401, detail="User not registered in any flat")
        
        result = belonging_dao.get_belonging(name, current_user.flat_code)
        
        if result is None:
            raise HTTPException(status_code=404, detail="belonging not found")

        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    
    
@belonging_router.get("/belonging/flat/all", response_model=List[belonging.BelongingStr], tags=["belonging"])
def get_belongings_in_flat(current_user: user.AuthUser = Depends(get_current_user)):
    try:
        
        if current_user.flat_code is None:
            raise HTTPException(status_code=401, detail="User not registered in any flat")
        
        result = belonging_dao.get_belongings_by_flat(current_user.flat_code)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    
    
@belonging_router.get("/belonging/user/all", response_model=List[belonging.BelongingStr], tags=["belonging"])
def get_belongings_of_user(current_user: user.AuthUser = Depends(get_current_user)):
    try:
        
        if current_user.flat_code is None:
            raise HTTPException(status_code=401, detail="User not registered in any flat")
        
        result = belonging_dao.get_belongings_by_flatmate(current_user.username, current_user.flat_code)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))