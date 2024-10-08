from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from models import User , Token
from utils import create_access_token, get_password_hash, verify_password, get_user
from database import cursor, conn  # SQLite connection
import sqlite3
from pydantic import EmailStr
 
from datetime import timedelta

SECRET_KEY = "8d9d1e837bc56b07f7e1db15fe3a69b02b8c3a8f7f9261dcb7f556b5261a97ba"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()

# request)
@router.post("/auth/register", response_model=dict)
async def register(user: User):
    # Check if the email exists
    cursor.execute("SELECT * FROM users WHERE email = ?", (user.email,))
    existing_user = cursor.fetchone()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Ensure password and confirm_password match
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    hashed_password = get_password_hash(user.password)
    role = user.role if user.role else "student"

    try:
        # Insert user into the database
        cursor.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                       (user.username, user.email, hashed_password, role))
        conn.commit()
        return {"message": "User registered successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already registered")



# Login route (returns JWT token in JSON format)
@router.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    cursor.execute("SELECT * FROM users WHERE username = ? OR email= ?", (form_data.username,form_data.username))
    user = cursor.fetchone()
    
    if not user or not verify_password(form_data.password, user[3]):  # user[3] is hashed password
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}