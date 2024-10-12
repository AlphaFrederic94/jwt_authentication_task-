from fastapi import APIRouter, Depends, HTTPException
from models import Grade
from utils import get_current_user
from database import cursor, conn

router = APIRouter()

# Get grades (returns JSON response)
# still working on this part
@router.get("/grades", response_model=Grade)
async def get_grades(current_user = Depends(get_current_user)):
    if current_user[3] != 'student':
        raise HTTPException(status_code=403, detail="Not authorized")
    
    cursor.execute("SELECT pure_maths, chemistry, biology, computer_science, physics FROM grades WHERE student_id=?", (current_user[0],))
    grades = cursor.fetchone()
    if not grades:
        raise HTTPException(status_code=404, detail="No grades found")
    return Grade(pure_maths=grades[0], chemistry=grades[1], biology=grades[2], computer_science=grades[3], physics=grades[4])

@router.put("/grades/{student_id}")
async def update_grades(student_id: int, grade: Grade, current_user = Depends(get_current_user)):
    # Check if the user is a teacher
    if current_user[1] != 'teacher':
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check if the student exists in the users table
    cursor.execute("SELECT id FROM users WHERE id = ?", (student_id,))
    student = cursor.fetchone()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Insert or update the student's grades
    cursor.execute("""
        INSERT OR REPLACE INTO grades (student_id, pure_maths, chemistry, biology, computer_science, physics) 
        VALUES (?, ?, ?, ?, ?, ?)
        """, 
        (student_id, grade.pure_maths, grade.chemistry, grade.biology, grade.computer_science, grade.physics))
    conn.commit()
    cursor.execute("""SELECT * FROM grades WHERE student_id = ?""",
                   (student_id,))
    updated_grade= cursor.fetchone()
    if(updated_grade and 
       updated_grade[1]== grade.pure_maths and
       updated_grade[2]== grade.chemistry and
       updated_grade[3]== grade.biology and
       updated_grade[4]== grade.computer_science and
       updated_grade[5]== grade.physics ):

        return {"message": "Grades updated successfully"}
    else:
      raise
HTTPException(status_code=500,detail="failed to update grades")

# Get top students (returns JSON)
@router.get("/top-students", response_model=list)
async def get_top_students():
    cursor.execute("SELECT student_id, (pure_maths + chemistry + biology + computer_science + physics) / 5 as avg_mark FROM grades ORDER BY avg_mark DESC LIMIT 5")
    top_students = cursor.fetchall()
    return [{"student_id": student[0], "average_mark": student[1]} for student in top_students]