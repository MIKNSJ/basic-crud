from typing import Annotated
from fastapi import FastAPI, Form, Request, Response, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
import authentication as auth
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import utilities as util

util.models.Base.metadata.create_all(bind=engine)
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name = "static")
templates = Jinja2Templates(directory="templates")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

id = 1;

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html");


@app.get("/clean")
async def clean_data(db: Session = Depends(get_db)):
    all_users = util.get_users(db);
    all_items = util.get_items(db)

    for user in all_users:
        db.delete(user);

    for item in all_items:
        db.delete(item)

    db.commit();
    return {"Database": "emptied"}


@app.get("/account", response_class=HTMLResponse)
async def account(request: Request):
    return templates.TemplateResponse(request=request, name="account.html");


@app.get("/account/create", response_class=HTMLResponse)
async def read_create(request: Request):
    return templates.TemplateResponse(request=request, name="create.html");


@app.post("/account/create/result")
async def post_create(db: Session = Depends(get_db), username: str = Form(), password: str = Form()):
    db_user = util.get_user(db, user_username=username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This user already exists.")

    #user_entry = auth.UserCreate(username = username, hashed_password = auth.get_password_hash(password))
    #auth.users_db[username] = user_entry;
    #return RedirectResponse("/account", status_code=status.HTTP_303_SEE_OTHER);

    new_user = util.models.User(username=username, hashed_password = auth.get_password_hash(password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    #return new_user
    return RedirectResponse("/account", status_code=status.HTTP_303_SEE_OTHER);


@app.get("/account/login", response_class=HTMLResponse)
async def read_login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html");


@app.post("/account/login/result")
async def login(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},)

    access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    #response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return auth.Token(access_token = access_token, token_type = "bearer");


@app.get("/account/self", response_model=util.schemas.User)
async def read_users_self(current_user: Annotated[util.schemas.User, Depends(auth.get_current_active_user)],):
    return current_user


@app.get("/account/self/items/")
async def read_own_items(current_user: Annotated[util.schemas.User, Depends(auth.get_current_active_user)],):
    return [{"owner": current_user.username, "hash": current_user.hashed_password}]


@app.post("/submit")
async def post_form(current_user: Annotated[util.schemas.User, Depends(auth.get_current_active_user)],
        db: Session = Depends(get_db),
        name: str = Form(), email: str = Form(), address: str = Form(), phone: str = Form(), count: str = Form()):
    global id;
    new_item = util.models.Item(id=id, name=name, email=email, address=address, phone=phone, count=count,
            owner_username=current_user.username)
    id+=1;
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER);


@app.get("/edit/{user_id}", response_class=HTMLResponse)
async def read_edit(user_id: int, request: Request, db: Session = Depends(get_db)):
    #edit_user = []
    #for user in user_data:
    #    if user["id"] == user_id:
    #        edit_user.append(user)

    curr_item = util.get_item(db, user_id)
    return templates.TemplateResponse(request=request, name="edit.html", context=curr_item);


@app.post("/resubmit/{user_id}")
async def change_form(user_id: int, db: Session = Depends(get_db), name: str = Form(), email: str = Form(), address: str = Form(), phone: str = Form(), count: str = Form()):
    curr_item = util.get_item(db, user_id)

    if curr_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    curr_item.name = name
    curr_item.email = email
    curr_item.address = address
    curr_item.phone = phone
    curr_item.count = count
    db.commit()
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/delete/{user_id}")
async def delete(user_id: int, db: Session = Depends(get_db)):
    curr_item = util.get_item(db, user_id)
    db.delete(curr_item)
    db.commit();
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
