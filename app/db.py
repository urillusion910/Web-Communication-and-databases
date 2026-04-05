import os, psycopg

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg.connect(DATABASE_URL, autocommit=True, row_factory=psycopg.rows.dict_row)

def create_schema():
    try:
        with get_conn() as conn, conn.cursor() as cur:
            # Create the schema
            cur.execute("""
                CREATE TABLE IF NOT EXISTS hotel_rooms (
                    id SERIAL PRIMARY KEY,
                    room_number INT NOT NULL UNIQUE,
                    type VARCHAR(50) NOT NULL,
                    price NUMERIC(10,2) NOT NULL CHECK (price >= 0)
                    );
            
                CREATE TABLE IF NOT EXISTS hotel_guests (
                    id SERIAL PRIMARY KEY,
                    firstname VARCHAR(100) NOT NULL,
                    lastname VARCHAR(100) NOT NULL,
                    address VARCHAR(255)
                    );
                        
                CREATE TABLE IF NOT EXISTS hotel_bookings (
                    id SERIAL PRIMARY KEY,
                    guest_id INT NOT NULL,
                    room_id INT NOT NULL,
                    datefrom DATE NOT NULL,
                    dateto DATE NOT NULL,
                    addinfo VARCHAR(255),
                    
                    CONSTRAINT fk_guest
                        FOREIGN KEY (guest_id)
                        REFERENCES hotel_guests(id)
                        ON DELETE CASCADE,

                    CONSTRAINT fk_room
                        FOREIGN KEY (room_id)
                        REFERENCES hotel_rooms(id)
                        ON DELETE CASCADE,
                        
                    CONSTRAINT valid_date CHECK (dateto > datefrom)
                    )""")
           
            # insert sample data
            cur.execute("""
                -- Rooms
                INSERT INTO hotel_rooms (room_number, type, price) VALUES
                (101, 'single', 80.00),
                (102, 'double', 120.00),
                (201, 'suite', 250.00);

                -- Guests
                INSERT INTO hotel_guests (firstname, lastname, address) VALUES
                ('John', 'Doe', '123 Main St'),
                ('Jane', 'Smith', '456 Oak Ave');

                -- Bookings
                INSERT INTO hotel_bookings (guest_id, room_id, datefrom, dateto, addinfo) VALUES
                (1, 1, '2026-04-10', '2026-04-15', 'Late arrival'),
                (2, 2, '2026-05-01', '2026-05-05', NULL)""")

    except Exception as e:
        print(f"Error while creating schema: {e}")