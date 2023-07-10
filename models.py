from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, SMALLINT
from sqlalchemy.orm import relationship

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

    products = relationship("Product", back_populates="owner")


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    for_which_gender = Column(String(10), nullable=False)
    Category = Column(Integer, nullable=False)
    sizes = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    description = Column(String(255), nullable=False)
    made_in_india = Column(Integer)
    state = Column(String(50))
    added_by = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="products")
