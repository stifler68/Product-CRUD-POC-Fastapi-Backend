from sqlalchemy import Boolean, Column, Date, Integer, String, SMALLINT
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(15), unique=True, nullable=False)
    alternate_number = Column(String(15))
    dob = Column(String(15), nullable=False)
    gender = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    state = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    nationality = Column(Integer, nullable=False)
