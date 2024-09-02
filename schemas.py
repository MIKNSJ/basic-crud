from pydantic import BaseModel


class Item(BaseModel):
    name: str
    email: str
    address: str
    phone: str
    count: str
    owner_username: str


    class Config:
        orm_mode = True


class User(BaseModel):
    username: str
    hashed_password: str
    is_active: bool
    items: list[Item] = []

    class Config:
        orm_mode = True
