from typing import Annotated
from fastapi import FastAPI, Form, Request, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
import authentication as auth

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name = "static")
templates = Jinja2Templates(directory="templates")

user_data = []
id = 1;

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context = {"user_data": user_data});


@app.get("/clean")
async def clean_users():
    user_data.clear();
    auth.users_db.clear();
    return {"Clean": "Success"}


@app.get("/account", response_class=HTMLResponse)
async def account(request: Request):
    return templates.TemplateResponse(request=request, name="account.html");


@app.get("/account/create", response_class=HTMLResponse)
async def read_create(request: Request):
    return templates.TemplateResponse(request=request, name="create.html");


@app.post("/account/create/result")
async def post_create(username: str = Form(), password: str = Form()):
    if username in auth.users_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This user already exists.")

    user_entry = auth.UserCreate(username = username, hashed_password = auth.get_password_hash(password))
    auth.users_db[username] = user_entry;
    return RedirectResponse("/account", status_code=status.HTTP_303_SEE_OTHER);


@app.get("/account/login", response_class=HTMLResponse)
async def read_login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html");


@app.post("/account/login/result")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],):
    user = auth.authenticate_user(auth.users_db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},)

    access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return auth.Token(access_token = access_token, token_type = "bearer");


@app.get("/account/self/", response_model=auth.UserCreate)
async def read_users_self(
    current_user: Annotated[auth.UserCreate, Depends(auth.get_current_active_user)],):
    return current_user


@app.get("/account/self/items/")
async def read_own_items(current_user: Annotated[auth.UserCreate, Depends(auth.get_current_active_user)],):
    return [{"owner": current_user.username, "hash": current_user.hashed_password}]


@app.post("/submit")
async def post_form(name: str = Form(), email: str = Form(), address: str = Form(), phone: str = Form(), count: str = Form()):
    global id;
    user_data.append({"id": id, "name": name, "email": email, "address": address, "phone": phone, "count": count})
    id+=1;
    print("User has signed up for supply package.");
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER);


@app.get("/edit/{user_id}", response_class=HTMLResponse)
async def read_edit(request: Request, user_id: int):
    edit_user = []
    for user in user_data:
        if user["id"] == user_id:
            edit_user.append(user)

    return templates.TemplateResponse(request=request, name="edit.html", context = {"edit_user": edit_user});


@app.post("/resubmit/{user_id}")
async def change_form(user_id: int, name: str = Form(), email: str = Form(), address: str = Form(), phone: str = Form(), count: str = Form()):
    for i in range(len(user_data)):
        if user_data[i]["id"] == user_id:
           user_data[i] = {"id": user_id, "name": name, "email": email, "address": address, "phone": phone, "count": count}

    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/delete/{user_id}")
async def delete(user_id: int):
    for user in user_data:
        if user["id"] == user_id:
            user_data.remove(user)

    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
