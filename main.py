from fastapi import Depends, FastAPI, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware

import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "https://example.com",
    "http://test.example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
def get_all_user(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    to_return = {
        "message": "User retrieved successfully",
        "data": users,
        "code": 200,
        "success": "true",
    }
    return to_return


@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_id(db, user_id=user_id)
    if db_user is None:
        return {"message": "User Not Found"}
    to_return = {
        "message": "User retrieved successfully",
        "data": db_user,
        "code": 200,
        "success": "true",
    }
    return to_return


@app.post("/users")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.create_user(db=db, user=user)
    if db_user == "phone_not_valid":
        to_return = {
            "message": "Phone Number is not a valid",
            "code": 400,
            "success": "false",
        }
        return to_return

    elif db_user == "email_already_exits":
        to_return = {
            "message": "Email Already exists",
            "code": 400,
            "success": "false",
        }
        return to_return
    else:
        to_return = {
            "message": "User Added Successfully",
            "data": db_user,
            "code": 200,
            "success": "true",
        }
        return to_return


@app.put("/users/{user_id}")
def update_user(user: schemas.UserUpdate, user_id: int, db: Session = Depends(get_db)):
    db_user = crud.update_user(db, user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user == "phone_not_valid":
        to_return = {
            "message": "Phone Number is not a valid",
            "code": 400,
            "success": "false",
        }
        return to_return
    else:
        return {"message": "Updated Successful"}


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.delete_user(db, user_id=user_id)
    message = {"Message": " User Deleted Successfully"}
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return message


# ----------------- Login ----------------------


@app.post("/users/login")
def login(user: schemas.Login, db: Session = Depends(get_db)):
    db_user = crud.user_login(db=db, user=user)
    message = {"Message": " Login Successful"}
    if db_user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    access_token = crud.create_access_token(data={"sub": db_user.email})
    return {
        "Message": " Login Successful",
        "access_token": access_token,
        "token_type": "bearer",
    }


@app.post("/token")
def read_user_me(current_user: str = Depends(crud.verify_token)):
    db = SessionLocal()
    db_user = db.query(models.User).filter(models.User.email == current_user).first()
    db.close()
    return db_user
