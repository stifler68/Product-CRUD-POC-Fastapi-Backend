from typing import Union
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


class Show_User(BaseModel):  # show all field to the user except password.
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


# ------------- PRODUCT ---------------------------------------------------------------


class Product(BaseModel):
    product_id: int
    name: str
    for_which_gender: str
    Category: int
    sizes: str
    quantity: int
    description: str
    made_in_india: int
    state: str
    added_by = int

    class Config:
        orm_mode = True


class ProductCreate(BaseModel):
    name: str
    for_which_gender: str
    Category: int
    sizes: str
    quantity: int
    description: str
    made_in_india: int
    state: str

    class Config:
        orm_mode = True


class ProductUpdate(BaseModel):
    name: Optional[str]
    for_which_gender: Optional[str]
    Category: Optional[int]
    sizes: Optional[str]
    quantity: Optional[int]
    description: Optional[str]
    made_in_india: Optional[int]
    state: Optional[str]

    class Config:
        orm_mode = True


# ------------------- ApiResponse ----------------


class ApiResponse(BaseModel):
    message: Optional[str]
    data: Union[list, dict] = []
    status_code: int = 200
    success: bool = True

    class Config:
        orm_mode = True
