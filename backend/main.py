from fastapi import FastAPI
from backend.database import init_db


app = FastAPI()

# Veritabanı başlatma
init_db()

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/health")
def health():
    return {"status": "ok"}

