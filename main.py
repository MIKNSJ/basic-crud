# from typing import Union
from fastapi import FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name = "static")
templates = Jinja2Templates(directory="templates")

user_data = [];
id = 1;

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context = {"user_data": user_data});


@app.get("/clean")
async def clean_users():
    user_data.clear();
    return {"Clean": "Success"}


@app.post("/templates")
async def post_form(name: str = Form(), email: str = Form(), address: str = Form(), phone: str = Form(), count: str = Form()):
    global id;
    user_data.append({"id": id, "name": name, "email": email, "address": address, "phone": phone, "count": count})
    id+=1;
    print("User has signed up for supply package.");
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER);


@app.get("/delete/{user_id}")
async def delete(user_id: int):
    for user in user_data:
        if user["id"] == user_id:
            user_data.remove(user)

    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER);
