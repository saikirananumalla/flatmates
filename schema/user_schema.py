from pydantic import BaseModel


class User(BaseModel):

    user_name: str
    email_id: str
    phone: str
    password: str

    class Config:
        orm_mode = True
