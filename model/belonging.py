from pydantic import BaseModel

class Belonging(BaseModel):
    belonging_id: int
    description: str
    name: str
    flat_code: str

class BelongingOwner(BaseModel):
    username: str

class BelongingWithOwner(BaseModel):
    belonging: Belonging
    owners: List[BelongingOwner]
    