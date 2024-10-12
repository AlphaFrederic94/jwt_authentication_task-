from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from models import User, Token
from utils import create_access_token, get_password_hash, verify_password, get_current_user
from database import cursor, conn  # SQLite connection
import sqlite3
from pydantic import EmailStr
from datetime import timedelta

SECRET_KEY = "8d9d1e837bc56b07f7e1db15fe3a69b02b8c3a8f7f9261dcb7f556b5261a97ba"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()

# Registration Route
@router.post("/auth/register", response_model=dict)
async def register(user: User):
   
   
    hashed_password = get_password_hash(user.password)
    role = user.role if user.role else "student"

    try:
        # Insert user into the database (fixed SQL statement)
        cursor.execute(
            "INSERT INTO users (firstName, lastName, email, password, dateOfBirth, role) VALUES (?, ?, ?, ?, ?, ?)",
            (user.firstName, user.lastName, user.email, hashed_password, user.dateOfBirth, role)
        )
        conn.commit()
        return {"message": "User registered successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail=" email already registered")
    

@router.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Query to check if the user with the provided email exists
    cursor.execute("SELECT * FROM users WHERE email = ?", (form_data.username,))
    user = cursor.fetchone()
    
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email ")  # Email not found
    
    # Assuming user[] is the hashed password in the database
    if not verify_password(form_data.password, user[4]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")  # Incorrect password

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user[3]},  # Assuming user[3] is the email column
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# TO tetrieve all users of the system 

@router.get("/students")
async def get_all_students(current_user = Depends(get_current_user)):

    # we check if the user is a teacher
    if current_user[1] != 'teacher':
        raise
    HTTPException(status_code=403,detail="Not authorized")

    cursor.execute("""SELECT email, firstName,lastName,dateOfbirth From users""")
    students = cursor.fetchall()

    if not students:
        raise
    HTTPException(status_code=404,detail="No students found")
    return[{"email":student[0],"firstName":student[1] ,"lastName":student[2],"dateOfbirth":student[3]} for student in students]

# to edit a particular student in the database with the password


#still working on this part


@router.put("/students/{student_id}")
async def update_student(student_id: int, updated_student: User, new_password:str = None, current_user= Depends(get_current_user)):
    # Check if the user is a teacher
    if current_user[1] != 'teacher':
        raise
    HTTPException(status_code=405,detail="Not authorized")

    cursor.execute("SELECT * FROM users WHERE id = ?" ,(student_id,))
    student = cursor.fetchone()
    if not student:
        raise
    HTTPException(status_code=406,detail="student not found")

    #we check if a new password have been provided then hash it

    if new_password:
        hashed_password= get_password_hash(new_password)
    else:
        hashed_password= student[4]
   
    try:
        cursor.execute ("""UPDATE users SET firstName = ?, lastName = ?, dateOfbirth = ?, password = ?  WHERE id = ?"""
                        ,(update_student.firstName,update_student.lastName,update_student.email,update_student.dateOfbirth,update_student.password, student_id))
        conn.commit()

        return{"message": "student updated succesfully"}
    except sqlite3.Error as e:
        raise
    HTTPException(status_code=500, detail="Failed to update student:{str(e)}")   