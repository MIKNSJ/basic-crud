from sqlalchemy.orm import Session
import models, schemas


def get_user(db: Session, user_username: str):
    return db.query(models.User).filter(models.User.username == user_username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


# def create_user(db: Session, user: schemas.User):
#     fake_hashed_password = user.password + "notreallyhashed"
#     db_user = models.User(username=user.username, hashed_password=fake_hashed_password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user

def get_item(db: Session, id: int):
    return db.query(models.Item).filter(models.Item.id == id).first()

def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


# def create_user_item(db: Session, item: schemas.Item, user_username: str):
#     db_item = models.Item(**item.dict(), owner_username=user_username)
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item
