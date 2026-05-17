from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import random
import string
import sqlite3
import os
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8080")


# Database setup FIRST
conn = sqlite3.connect("urls.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS urls (
        short_code TEXT PRIMARY KEY,
        original_url TEXT NOT NULL
    )
""")
conn.commit()

app = FastAPI()

def generate_short_code():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

@app.get("/")
def home():
    return FileResponse("index.html")

@app.post("/shorten")
def shorten_url(url: str):
    
    cursor.execute("SELECT short_code FROM urls WHERE original_url = ?", (url,))
    result = cursor.fetchone()
    
    if(result):
        short_code = result[0]
    else:
        short_code = generate_short_code()
        cursor.execute("INSERT INTO urls VALUES (?, ?)", (short_code, url))
        conn.commit()
    
    return {
        "short_code": short_code,
        "short_url": f"{BASE_URL}/{short_code}"
    }

@app.get("/{short_code}")
def redirect_to_original(short_code: str):
    
    

    cursor.execute("SELECT original_url FROM urls WHERE short_code = ?", (short_code,))
    result = cursor.fetchone()
    if result:
        return RedirectResponse(url=result[0], status_code=307)
    raise HTTPException(status_code=404, detail="Short URL not found")