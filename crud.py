import json
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
import models, schemas
from response_parser import generate_response

from passlib.context import CryptContext

# Authentication
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    OAuth2AuthorizationCodeBearer,
)
from jose import JWTError, jwt
from passlib.context import CryptContext
from jwt import InvalidTokenError, ExpiredSignatureError
import crud, models, schemas

#
import os
from dotenv import load_dotenv


load_dotenv()


oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="token", tokenUrl="token"
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_users(db: Session, skip: int = 0, limit: int = 100):
    user = db.query(models.User).offset(skip).limit(limit).all()
    to_return = []
    for i in user:
        to_return.append(json.loads(schemas.Show_User.parse_obj(i.__dict__).json()))

    return to_return


def create_user(db: Session, user: schemas.UserCreate):
    if user.password:
        user.password = pwd_context.hash(user.password)

    user_data = user.dict()
    db_user = models.User(**user_data)

    email = user.email
    check_email = db.query(models.User).filter(models.User.email == email).first()
    if len(db_user.phone_number) != 10 or (
        len(db_user.alternate_number) != 0 and len(db_user.alternate_number) != 10
    ):
        return "phone_not_valid"
    elif check_email:
        return "email_already_exits"

    else:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user


def get_user_by_id(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    to_return = []

    to_return = []
    to_return.append(json.loads(schemas.Show_User.parse_obj(user.__dict__).json()))

    return to_return


def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    if user.password:
        user.password = pwd_context.hash(user.password)

    filtered_payload = {
        key: value for key, value in dict(user).items() if value != None
    }
    if "phone_number" in filtered_payload.keys():
        if len(filtered_payload["phone_number"]) != 10 or (
            len(filtered_payload["alternate_number"]) != 0
            and len(filtered_payload["alternate_number"]) != 10
        ):
            return "phone_not_valid"
    val = (
        db.query(models.User).filter(models.User.id == user_id).update(filtered_payload)
    )
    db.commit()
    return val


def delete_user(db: Session, user_id: int):
    user_found = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_found:
        return user_found
    db.delete(user_found)
    db.commit()
    return user_found


def user_login(db: Session, user: schemas.Login):
    user_found = db.query(models.User).filter(models.User.email == user.email).first()

    if user_found is None:
        raise generate_response(
            message="User does not exists.", success=False, code=404
        )

    if not pwd_context.verify(user.password, user_found.password):
        # print(user_found.__dict__)
        raise generate_response(message="Invalid credentials.", success=False, code=400)

    access_token = crud.create_access_token(data={"sub": user_found.email})
    return generate_response(
        message="Login success. ",
        success=True,
        data={"name": user_found.email, "access_token": access_token},
    )


# Configure JWT setting
# getting data from .env file
SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")


# Generate a JWT access token
def create_access_token(data: dict):
    to_encode = data.copy()
    access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return access_token


def verify_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload["sub"]
        # Fetch the user from the database based on the username or perform other operations as needed
        if email is None:
            return {"Error": " User not Found"}
        user = db.query(models.User).filter(models.User.email == email).first()
        if user:
            return user
        return {"Error": " User not Found"}
    except JWTError:
        return {"Error": " Username not Found"}


# Hash a password
def get_password_hash(password):
    return pwd_context.hash(password)


# Verify a password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# ----------------------- Products ---------------------------------------


def get_all_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()


def get_product_by_Id(db: Session, product_id: int):
    return (
        db.query(models.Product).filter(models.Product.product_id == product_id).first()
    )


def add_product(db: Session, product: schemas.ProductCreate, added_by: int):
    api_product = {**product.dict()}
    api_product["added_by"] = added_by

    db_product = models.Product(**api_product)
    if db_product.made_in_india == 1 and len(db_product.state) <= 0:
        return "state_error"
    if db_product.made_in_india == 0 and len(db_product.state) > 0:
        return "country_error"

    db.add(db_product)
    db.flush()
    db.commit()
    db.refresh(db_product)

    return db_product.__dict__


def delete_product(db: Session, product_id: int):
   
    product_found = (
        db.query(models.Product).filter(models.Product.product_id == product_id).first()
    )
 
    if not product_found:
        return product_found
    db.delete(product_found)
    db.commit()

    return product_found


def update_product(db: Session, product_id: int, product: schemas.ProductUpdate):
    filtered_payload = {
        key: value for key, value in dict(product).items() if value != None
    }

    val = (
        db.query(models.Product)
        .filter(models.Product.product_id == product_id)
        .update(filtered_payload)
    )
    db.commit()
    return val
