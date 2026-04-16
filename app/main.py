
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.db import *
from datetime import date

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    create_schema()
    return { "msg": "Hello World!", "v": "0.1" }


@app.get("/items/{id}")
def read_item(item_id: int, q: str = None):
    return {"id": id, "q": q}

@app.get("/api/ip")
async def get_ip_json(request: Request):
    client_ip = request.client.host
    return {"ip": client_ip}

@app.get("/ip", response_class=HTMLResponse)
async def get_ip_html(request: Request):
    client_ip = request.client.host
    html_content = f"<h1>Your public IP is {client_ip}</h1>"
    return html_content

# List all rooms 
@app.get("/rooms")
def get_rooms(): 
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM hotel_rooms")
        rooms = cur.fetchall()
    return rooms

# Get one room
@app.get("/rooms/{id}")
def get_one_room(id: int): 
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT * 
            FROM hotel_rooms 
            WHERE id = %s
        """, (id,)) # <- tuple, list is also fine: [id]
        room = cur.fetchone()
    return room

# List all bookings 
@app.get("/bookings")
def get_bookings(): 
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
           SELECT
                b.datefrom, 
                (b.dateto - b.datefrom) AS days,
                b.addinfo,
                r.room_number,
                g.firstname
            FROM hotel_bookings b
            JOIN hotel_rooms r ON b.room_id = r.id
            JOIN hotel_guests g ON b.guest_id = g.id        
        """)
        b = cur.fetchall()
    return b


# Data model for bookings
class Booking(BaseModel):
    guest_id: int
    room_id: int
    datefrom: date
    dateto: date
    addinfo: str = None

# Create booking
@app.post("/bookings")
def create_booking(booking: Booking):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO hotel_bookings (
                room_id, 
                guest_id,
                datefrom,
                dateto,
                addinfo
            ) VALUES (
                %s, %s, %s, %s, %s
            ) RETURNING *
        """, [
            booking.room_id, 
            booking.guest_id,
            booking.datefrom,
            booking.dateto,
            booking.addinfo
        ])
        new_booking = cur.fetchone()
        
    return { 
        "msg": "Booking created!", 
        "id": new_booking['id'],
        "room_id": new_booking['room_id']
    }

@app.get("/guests")
def get_guests(): 
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
                SELECT *,
                    (SELECT COUNT(*) 
                    FROM hotel_bookings b 
                    WHERE b.guest_id = g.id AND b.dateto < CURRENT_DATE
                    ) AS previous_visits
                FROM hotel_guests g
            """)
        guests = cur.fetchall()
    return guests

@app.get("/guests/{id}")
def get_guest(id: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
                SELECT COUNT(*) 
                FROM hotel_bookings b 
                WHERE b.guest_id = %s AND b.dateto < CURRENT_DATE
            """, (id,))
        guest = cur.fetchone()
    return guest