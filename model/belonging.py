from pydantic import BaseModel
from pydantic.schema import List
from typing import Optional

class UpdateBelonging(BaseModel):
    description: Optional[str]
    name: str
    owners: Optional[List[str]]

class Belonging(UpdateBelonging):
    flat_code: str
    
class BelongingStr(BaseModel):
    belonging_id: int
    description: Optional[str]
    name: str
    flat_code: str
    owners: Optional[str]
    
class BelongingWithId(Belonging):
    belonging_id: int
    