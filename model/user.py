from pydantic import BaseModel, EmailStr, constr


class User(BaseModel):
    username: str
    email_id: constr(regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    phone: constr(regex=r'^\d{10}$')

class UserWithPassword(User):
    password: str
