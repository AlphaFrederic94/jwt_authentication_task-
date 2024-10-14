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
    
    # Assuming user[4] is the hashed password in the database
    if not verify_password(form_data.password, user[4]):
        raise HTTPException(status_code=400, detail="Incorrect password")  # Incorrect password

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"email":user[3], "role":user[6]},  # Assuming user[3] is the email column
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# TO tetrieve all users of the system 

@router.get("/students")
async def get_all_students(current_user = Depends(get_current_user)):
    print(current_user)
    # we check if the user is a teacher
    if current_user[1] != 'teacher':
        raise
    HTTPException(status_code=403,detail="Not authorized")

    try:
        cursor.execute("""SELECT id, email, firstName, lastName, dateOfBirth FROM users WHERE role = 'student'""")
        students = cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

    if not students:
        raise HTTPException(status_code=404, detail="No students found")
    
    return [{"id": student[0], "email": student[1], "firstName": student[2], "lastName": student[3], "dateOfBirth": student[4] } for student in students]



@router.get("/teacher")
async def get_all_teacher(current_user = Depends(get_current_user)):
    print(current_user)
    # we check if the user is a teacher
    if current_user[1] != 'teacher':
        raise
    HTTPException(status_code=403,detail="Not authorized")

    try:
        cursor.execute("""SELECT id, email, firstName, lastName, dateOfBirth FROM users WHERE role = 'teacher'""")
        teachers = cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

    if not teachers:
        raise HTTPException(status_code=404, detail="No teachers found")
    
    return [{"id": teacher[0], "email": teacher[1], "firstName": teacher[2], "lastName": teacher[3], "dateOfBirth": teacher[4] } for teacher in teachers]



@router.delete("/students/{student_id}")
async def delete_student(student_id: int, current_user=Depends(get_current_user)):
        if current_user[1] !='teacher':
            raise HTTPException(status_code=406,detail="Not authorized to delete a student")
        
        cursor.execute("SELECT * FROM users WHERE id = ?",(student_id,))
        student = cursor.fetchone()
        if not student:
            raise HTTPException(status_code=407, detail="student not found")
        
        #delete the student from the table users
        try:
            cursor.execute("DELETE FROM users WHERE id = ?",(student_id,))
            conn.commit()

            #also we delete the student grades from the table grades

            cursor.execute("DELETE FROM grades WHERE student_id = ?",(student_id,))
            conn.commit()

            return {"message":" Student and their grades have been successfully deleted"}
        except sqlite3.Error as e:
            raise HTTPException(status_code=500, detail=f"an error occured:{str(e)}")


# to edit a particular student in the database with the password

#still working on this part


@router.put("/students/{student_id}")
async def update_profile(user_update: User, current_user = Depends(get_current_user)):
    if current_user[1] != 'teacher':
        raise HTTPException(status_code=403, detail="Only teachers can update their own profile")
    
    try:
        updates = {}
        if user_update.firstName:
            updates['firstName'] = user_update.firstName
        if user_update.lastName:
            updates['lastName'] = user_update.lastName
        if user_update.email:
            updates['email'] = user_update.email
        if user_update.dateOfBirth:
            updates['dateOfBirth'] = user_update.dateOfBirth
        if user_update.password:
            updates['password'] = get_password_hash(user_update.password)
        
        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        set_clause = ", ".join(f"{key} = ?" for key in updates)
        query = f"UPDATE users SET {set_clause} WHERE email = ?"
        
        cursor.execute(query, (*updates.values(), current_user[0]))
        conn.commit()
        
        return {"message": "Profile updated successfully"}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")


# "email":user[3],"dateOfbirth":user[5],