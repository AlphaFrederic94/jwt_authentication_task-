from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Grade, User  # Ensure you import User
from app.schemas import GradeUpdateSchema

# Create a Blueprint for grades
routes = Blueprint('grades', __name__)

@routes.route('/', methods=['GET'])
@jwt_required()
def get_grades():
    current_user = get_jwt_identity()
    grades = Grade.query.filter_by(student_id=current_user['id']).first()
    
    if not grades:
        return jsonify({"message": "Grades not found"}), 404
    
    return jsonify({
        "pure_maths": grades.pure_maths,
        "chemistry": grades.chemistry,
        "biology": grades.biology,
        "computer_science": grades.computer_science,
        "physics": grades.physics
    }), 200

@routes.route('/<int:student_id>', methods=['PUT'])
@jwt_required()
def update_grades(student_id):
    current_user = get_jwt_identity()
    if current_user['role'] not in ['teacher', 'admin']:
        return jsonify({"message": "Permission denied"}), 403

    json_data = request.get_json()
    errors = GradeUpdateSchema().validate(json_data)
    if errors:
        return jsonify(errors), 400

    grades = Grade.query.filter_by(student_id=student_id).first()
    if not grades:
        return jsonify({"message": "Student grades not found"}), 404

    for key, value in json_data.items():
        setattr(grades, key, value)
    
    db.session.commit()
    return jsonify({"message": "Grades updated successfully"}), 200

@routes.route('/top-students', methods=['GET'])
def get_top_students():
    students_with_grades = db.session.query(User, Grade).join(Grade, User.id == Grade.student_id).all()
    
    if not students_with_grades:
        return jsonify({"message": "No students or grades found"}), 404

    student_averages = []
    for student, grade in students_with_grades:
        total = (grade.pure_maths or 0) + (grade.chemistry or 0) + (grade.biology or 0) + \
                (grade.computer_science or 0) + (grade.physics or 0)
        avg = total / 5
        student_averages.append({
            "id": student.id,
            "name": student.username,
            "average": avg
        })

    top_students = sorted(student_averages, key=lambda x: x['average'], reverse=True)[:5]
    return jsonify({"top_students": top_students}), 200
