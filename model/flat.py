from pydantic import BaseModel

class Flat(BaseModel):
    flat_code: str
    name: str