# from typing import Union
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static", html = True), name = "static")
templates = Jinja2Templates(directory="templates")

user_data = [];
user_id = 1;

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context = {"user_data": user_data});


@app.get("/clean")
async def clean_users():
    user_data.clear();
    return {"Clean": "Success"}


@app.post("/templates")
async def post_form(request : Request, name: str = Form(), email: str = Form(), address: str = Form(), phone: str = Form(), count: str = Form()):
    global user_id;
    # user_data.append({"user_id": user_id, "name": name, "email": email, "address": address, "phone": phone, "count": count})
    user_id+=1;
    print("User has signed up for supply package.");
    redirect_url = request.url_for("read_root");
    return RedirectResponse("/");
