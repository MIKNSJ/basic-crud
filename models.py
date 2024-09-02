from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    items = relationship("Item", back_populates="owner")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    address = Column(String, index=True)
    phone = Column(String, index=True)
    count = Column(String, index=True)
    owner_username = Column(String, ForeignKey("users.username"))

    owner = relationship("User", back_populates="items")
