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
    # Check if grades already exist
    cursor.execute("SELECT * FROM grades WHERE student_id = ?", (student_id,))
    existing_grade = cursor.fetchone()
    
    if existing_grade:
        # Update existing grades
        cursor.execute("""
            UPDATE grades SET 
                pure_maths = ?, 
                chemistry = ?, 
                biology = ?, 
                computer_science = ?, 
                physics = ? 
            WHERE student_id = ?
        """, 
        (grade.pure_maths, grade.chemistry, grade.biology, grade.computer_science, grade.physics, student_id))
    else:
        # Insert new grades
        cursor.execute("""
            INSERT INTO grades (student_id, pure_maths, chemistry, biology, computer_science, physics) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, 
        (student_id, grade.pure_maths, grade.chemistry, grade.biology, grade.computer_science, grade.physics))


        return {"message": "Grades updated successfully"}
    
@router.get("/grades/{student_id}")
async def get_grades(student_id: int, current_user = Depends(get_current_user)):
    # Only teachers should access the grades
    if current_user[1] != 'teacher':
        raise HTTPException(status_code=403, detail="Not authorized")

    # Fetch the grades for the given student ID
    cursor.execute("SELECT * FROM grades WHERE student_id = ?", (student_id,))
    grade = cursor.fetchone()

    if not grade:
        raise HTTPException(status_code=404, detail="Grades not found for this student")
    
    return {
        "student_id": grade[0],
        "pure_maths": grade[1],
        "chemistry": grade[2],
        "biology": grade[3],
        "computer_science": grade[4],
        "physics": grade[5],
    }

# Get top students (returns JSON)
@router.get("/top-students", response_model=list)
async def get_top_students():
    query = """
    SELECT u.id, u.firstName, u.lastName, u.email, u.dateOfBirth, 
           (g.pure_maths + g.chemistry + g.biology + g.computer_science + g.physics) / 5 as avg_mark 
    FROM users u
    JOIN grades g ON u.id = g.student_id
    ORDER BY avg_mark DESC 
    LIMIT 5
    """
    cursor.execute(query)
    top_students = cursor.fetchall()
    return [{"id": student[0],"firstName": student[1],"lastName": student[2],"email": student[3], "dateOfBirth": student[4], "average_mark": student[5],} for student in top_students]