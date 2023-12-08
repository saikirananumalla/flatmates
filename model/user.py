from pydantic import BaseModel, EmailStr, constr
from typing import Optional


class User(BaseModel):
    username: str
    email_id: constr(regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    phone: constr(regex=r'^\d{10}$')


class UserWithPassword(User):
    password: str


class AuthUser(BaseModel):
    username: str
    flat_code: Optional[str]


class LoginForm(BaseModel):
    username: str
    password: str


class UpdateProfile(BaseModel):
    email_id: constr(regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    phone: constr(regex=r'^\d{10}$')
    password: str
