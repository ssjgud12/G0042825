from fastapi import Depends, FastAPI
from pytest import Session

from app.database import SessionLocal, get_db
from app.schemas import UserCreate

app = FastAPI(title="Example template")

@app.get("/health")
def health():
    return{"status": "ok"}

@app.post("api/requests")
def add_user(user: UserCreate, db: Session = 
Depends(get_db)):

   db = SessionLocal()

@app.get("api/requests")
def add_user(user: UserCreate, db: Session = 
Depends(get_db)):

    db = SessionLocal()
