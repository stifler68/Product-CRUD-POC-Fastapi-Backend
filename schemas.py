from pydantic import BaseModel, EmailStr
from typing import Optional

from sqlalchemy import Date


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    alternate_number: str
    dob: str
    gender: str
    address: str
    state: str
    password: str
    nationality: int

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    alternate_number: str
    dob: str
    gender: str
    address: str
    state: str
    password: str
    nationality: int

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]
    phone_number: Optional[str]
    alternate_number: Optional[str]
    dob: Optional[str]
    gender: Optional[str]
    address: Optional[str]
    state: Optional[str]
    password: Optional[str]
    nationality: Optional[int]

    class Config:
        orm_mode = True


class Login(BaseModel):
    email: EmailStr
    password: str

    class Config:
        orm_mode = True


class verify_token(BaseModel):
    token_number: str

    class Config:
        orm_mode = True
