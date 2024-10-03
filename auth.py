from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from models import User, Token
from utils import create_access_token, get_password_hash, verify_password, get_user
from database import cursor, conn
import sqlite3

SECRET_KEY = "8d9d1e837bc56b07f7e1db15fe3a69b02b8c3a8f7f9261dcb7f556b5261a97ba"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()

# Register route (uses JSON body for request)
@router.post("/auth/register", response_model=dict)
async def register(user: User):
    hashed_password = get_password_hash(user.password)
    role = user.role if user.role else "student"
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (user.username, hashed_password,role ))
        conn.commit()
        return {"message": "User registered successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already registered")

# Login route (returns JWT token in JSON format)
@router.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, user[2]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}