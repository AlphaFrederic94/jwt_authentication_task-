from flask import Blueprint, jsonify, request  # Import request from Flask
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import User, Grade  # Import User and Grade models
from app.schemas import GradeUpdateSchema  # Import GradeUpdateSchema

# Create a Blueprint for admin actions
routes = Blueprint('admin', __name__)

@routes.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"message": "Permission denied"}), 403
    
    users = User.query.all()
    return jsonify([{"id": user.id, "username": user.username, "role": user.role} for user in users]), 200

@routes.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"message": "Permission denied"}), 403
    
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200

@routes.route('/grades/<int:student_id>', methods=['PUT'])
@jwt_required()
def admin_update_grades(student_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({"message": "Permission denied"}), 403

    json_data = request.get_json()  # Use request to get the JSON data
    errors = GradeUpdateSchema().validate(json_data)  # Validate the incoming data
    if errors:
        return jsonify(errors), 400

    grades = Grade.query.filter_by(student_id=student_id).first()
    if not grades:
        return jsonify({"message": "Student grades not found"}), 404

    for key, value in json_data.items():
        setattr(grades, key, value)
    
    db.session.commit()
    return jsonify({"message": "Grades updated successfully"}), 200
