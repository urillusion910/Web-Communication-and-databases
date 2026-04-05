
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from app.db import *


app = FastAPI()

@app.get("/")
def read_root():
    create_schema()
    return { "msg": "Hello World!", "v": "0.1" }


@app.get("/items/{id}")
def read_item(item_id: int, q: str = None):
    return {"id": id, "q": q}


# Part 1: JSON Response
@app.get("/api/ip")
async def get_ip_json(request: Request):
    # request.client contains the host (IP) and port of the client
    client_ip = request.client.host
    return {"ip": client_ip}

# Part Two (Optional): HTML Response
@app.get("/ip", response_class=HTMLResponse)
async def get_ip_html(request: Request):
    client_ip = request.client.host
    # Using an f-string to inject the IP into the HTML tag
    html_content = f"<h1>Your public IP is {client_ip}</h1>"
    return html_content