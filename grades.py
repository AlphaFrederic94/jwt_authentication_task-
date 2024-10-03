from fastapi import APIRouter, Depends, HTTPException
from models import Grade
from utils import get_current_user
from database import cursor, conn

router = APIRouter()

# Get grades (returns JSON response)
@router.get("/grades", response_model=Grade)
async def get_grades(current_user = Depends(get_current_user)):
    if current_user[3] != 'student':
        raise HTTPException(status_code=403, detail="Not authorized")
    
    cursor.execute("SELECT pure_maths, chemistry, biology, computer_science, physics FROM grades WHERE student_id=?", (current_user[0],))
    grades = cursor.fetchone()
    if not grades:
        raise HTTPException(status_code=404, detail="No grades found")
    return Grade(pure_maths=grades[0], chemistry=grades[1], biology=grades[2], computer_science=grades[3], physics=grades[4])

# Update grades (accepts and returns JSON)
@router.put("/grades/{student_id}", response_model=dict)
async def update_grades(student_id: int, grade: Grade, current_user = Depends(get_current_user)):
    if current_user[3] != 'teacher':
        raise HTTPException(status_code=403, detail="Not authorized")

    cursor.execute("UPDATE grades SET pure_maths=?, chemistry=?, biology=?, computer_science=?, physics=? WHERE student_id=?", 
                   (grade.pure_maths, grade.chemistry, grade.biology, grade.computer_science, grade.physics, student_id))
    conn.commit()
    return {"message": "Grades updated successfully"}

# Get top students (returns JSON)
@router.get("/top-students", response_model=list)
async def get_top_students():
    cursor.execute("SELECT student_id, (pure_maths + chemistry + biology + computer_science + physics) / 5 as avg_mark FROM grades ORDER BY avg_mark DESC LIMIT 5")
    top_students = cursor.fetchall()
    return [{"student_id": student[0], "average_mark": student[1]} for student in top_students]