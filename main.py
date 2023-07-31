import json
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

import crud, models, schemas
from database import SessionLocal, engine

from response_parser import generate_response
from const import (
    INVALID_USERNAME_OR_PASSWORD,
    LOGIN_SUCCESSFUL,
    PLEASE_CHECK_MADE_IN_INDIA_AND_STATE_FIELD,
    PLEASE_PROVIDE_STATE_FIELD,
    PRODUCT_ADDED_SUCCESSFULLY,
    PRODUCT_DELETED_SUCCESSFULLY,
    PRODUCT_NOT_FOUND,
    PRODUCT_UPDATE_SUCCESSFULLY,
    UPDATED_SUCCESSFUL,
    USER_ADDED_SUCCESSFULLY,
    USER_DELETED_SUCCESSFULLY,
    USER_RETRIEVED_SUCCESSFULLY,
    USER_NOT_FOUND,
    PHONE_NUMBER_IS_NOT_VALID,
    EMAIL_ALREADY_EXISTS,
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# Configure CORS
origins = [
    "http://localhost:3000",
    "http://192.168.10.74",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "https://example.com",
    "http://test.example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/users")
def get_all_user(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: str = Depends(crud.verify_token),
):
    try:
        users = crud.get_users(db, skip=skip, limit=limit)

        to_return = {
            "message": USER_RETRIEVED_SUCCESSFULLY,
            "data": users,
            "code": 201,
            "success": "True",
        }
        return to_return
    except:
        return {"message": "Unknown Error Occurred"}


@app.get("/users/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(crud.verify_token),
):
    try:
        db_user = crud.get_user_by_id(db, user_id=user_id)
        if db_user is None:
            return {
                "message": USER_NOT_FOUND,
                "code": 404,
                "success": "true",
            }
        to_return = {
            "message": USER_RETRIEVED_SUCCESSFULLY,
            "data": db_user,
            "code": 200,
            "success": "true",
        }
        return to_return
    except:
        return {"message": "Unknown Error Occurred"}


@app.post("/users")
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    try:
        db_user = crud.create_user(db=db, user=user)
        if db_user == "phone_not_valid":
            to_return = {
                "message": PHONE_NUMBER_IS_NOT_VALID,
                "code": 400,
                "success": "false",
            }
            return to_return

        elif db_user == "email_already_exits":
            to_return = {
                "message": EMAIL_ALREADY_EXISTS,
                "code": 400,
                "success": "false",
            }
            return to_return
        else:
            to_return = {
                "message": USER_ADDED_SUCCESSFULLY,
                "data": db_user,
                "code": 200,
                "success": "true",
            }
            return to_return
    except:
        return {"message": "Unknown Error Occurred"}


@app.put("/users/{user_id}")
def update_user(
    user: schemas.UserUpdate,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(crud.verify_token),
):
    try:
        db_user = crud.update_user(db, user_id=user_id, user=user)
        if db_user is None:
            raise HTTPException(status_code=404, detail=USER_NOT_FOUND)
        if db_user == "phone_not_valid":
            to_return = {
                "message": PHONE_NUMBER_IS_NOT_VALID,
                "code": 400,
                "success": "false",
            }
            return to_return
        else:
            return {"message": UPDATED_SUCCESSFUL}
    except:
        return {"message": "Unknown Error Occurred"}


@app.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(crud.verify_token),
):
    try:
        db_user = crud.delete_user(db, user_id=user_id)
        message = {"Message": USER_DELETED_SUCCESSFULLY}
        if db_user is None:
            raise HTTPException(status_code=404, detail=USER_NOT_FOUND)
        return message
    except:
        return {"message": "Unknown Error Occurred"}


# ----------------- Login ------------------------------


@app.post("/login")
def login(user: schemas.Login, db: Session = Depends(get_db)):
    try:
        return crud.user_login(db=db, user=user)
        # message = {"Message": LOGIN_SUCCESSFUL}
        # if db_user is None:
        #     raise HTTPException(status_code=401, detail=INVALID_USERNAME_OR_PASSWORD)
        # access_token = crud.create_access_token(data={"sub": db_user.email})

        # return {
        #     "Message": LOGIN_SUCCESSFUL,
        #     "access_token": access_token,
        #     "token_type": "bearer",
        # }

    except Exception as err:
        if hasattr(err, "status_code"):
            raise err
        raise generate_response(message=f"Some error occurred", success=False, code=500)


# @app.post("/user-me")
# def read_user_me(
#     current_user: schemas.User = Depends(
#         crud.verify_token,
#     ),
#     db: Session = Depends(get_db),
# ):
#     db = SessionLocal()
#     db_user = db.query(models.User).filter(models.User.email == current_user).first()
#     db.close()
#     return db_user


# ----------------- PRODUCT --------------------------


@app.get("/products", response_model=list[schemas.Product])
def get_all_product(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: str = Depends(crud.verify_token),
):
    try:
        product = crud.get_all_products(db, skip=skip, limit=limit)
        return product
    except:
        return {"message": "Unknown Error Occurred"}


# Add Product
@app.post("/product")
def add_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(crud.verify_token),
):
    try:
        product_values = crud.add_product(
            db=db, product=product, added_by=current_user.id
        )

        if product_values == "state_error":
            to_return = {
                "message": PLEASE_PROVIDE_STATE_FIELD,
                "code": 400,
                "success": "False",
            }
            return to_return
        elif product_values == "country_error":
            to_return = {
                "message": PLEASE_CHECK_MADE_IN_INDIA_AND_STATE_FIELD,
                "code": 400,
                "success": "False",
            }
            return to_return
    except:
        return {"message": "Unknown Error Occurred"}

    to_return = {
        "message": PRODUCT_ADDED_SUCCESSFULLY,
        "code": 201,
        "success": "True",
    }
    return to_return


@app.get("/product/{product_id}", response_model=schemas.Product)
def get_product_by_ID(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(crud.verify_token),
):
    try:
        db_product = crud.get_product_by_Id(db=db, product_id=product_id)
        if db_product is None:
            raise HTTPException(status_code=404, detail=PRODUCT_NOT_FOUND)
        return db_product
    except:
        return {"message": "Unknown Error Occurred"}


@app.put("/product/{product_id}")
def update_product(
    product: schemas.ProductUpdate,
    product_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(crud.verify_token),
):
    try:
        db_product = crud.update_product(db=db, product_id=product_id, product=product)
        if db_product is None:
            raise HTTPException(status_code=404, detail=PRODUCT_NOT_FOUND)
        to_return = {
            "message": PRODUCT_UPDATE_SUCCESSFULLY,
            "code": 400,
            "success": "true",
        }
        return to_return
    except:
        return {"message": "Unknown Error Occurred"}


@app.delete("/product/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(crud.verify_token),
):
    try:
        db_product = crud.delete_product(db=db, product_id=product_id)
        if db_product is None:
            raise HTTPException(status_code=404, detail=USER_NOT_FOUND)
        print("---------------")
        to_return = {
            "message": PRODUCT_DELETED_SUCCESSFULLY,
            "code": 400,
            "success": "true",
        }
        return to_return
    except:
        return {"message": "Product Not Found"}
