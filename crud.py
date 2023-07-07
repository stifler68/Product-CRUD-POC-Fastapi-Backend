import json
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
import models, schemas

from passlib.context import CryptContext

# Authentication
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from jwt import InvalidTokenError, ExpiredSignatureError

#
import os
from dotenv import load_dotenv

load_dotenv()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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
        to_return.append(json.loads(schemas.User.parse_obj(i.__dict__).json()))

    return to_return


def create_user(db: Session, user: schemas.UserCreate):
    if user.password:
        user.password = pwd_context.hash(user.password)

    user_data = user.dict()
    db_user = models.User(**user_data)
    # print(type(db_user))
    # print(len(db_user.alternate_number), len(db_user.phone_number))
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
    print((user).__dict__)
    to_return = []
    to_return.append(json.loads(schemas.User.parse_obj(user.__dict__).json()))

    return to_return


def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    if user.password:
        user.password = pwd_context.hash(user.password)
    print(user)
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
    if not user_found:
        return None
    # print(user.password, "  --   ", user_found.password)
    if not pwd_context.verify(user.password, user_found.password):
        return None
    return user_found


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


# Verify the JWT access token
# def verify_token(token: schemas.verify_token, db: Session):
#     try:
#         print(">>>>")
#         payload = jwt.decode(token.token_number, SECRET_KEY, algorithms=[ALGORITHM])
#         email = payload["sub"]
#         print(email)
#         if email is None:
#             raise HTTPException(status_code=401, detail="Username not found")

#         # Fetch the user from the database based on the username or perform other operations as needed
#         user = db.query(models.User).filter(models.User.email == email).first()

#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")

#         to_return = []
#         to_return.append(json.loads(schemas.User.parse_obj(user.__dict__).json()))

#         return to_return

# except JWTError:
#     raise HTTPException(status_code=401, detail="Invalid token")


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


def add_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    print(db_product)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


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
    print(filtered_payload)
    val = (
        db.query(models.Product)
        .filter(models.Product.product_id == product_id)
        .update(filtered_payload)
    )
    db.commit()
    return val
