from typing import Union
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static", html = True), name = "static")


@app.get("/")
async def read_root():
    return {"Root": "Success"}

@app.get("/test")
async def read_test():
    return {"Test": "Success"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
