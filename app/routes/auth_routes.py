from flask import Blueprint, request, jsonify
from app import db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from app.schemas import UserCreateSchema, UserLoginSchema

# Create a Blueprint for authentication
routes = Blueprint('auth', __name__)

@routes.route('/register', methods=['POST'])
def register():
    json_data = request.get_json()
    errors = UserCreateSchema().validate(json_data)
    if errors:
        return jsonify(errors), 400

    username = json_data['username']
    password = json_data['password']
    role = json_data['role']

    # Check if user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password_hash=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@routes.route('/login', methods=['POST'])
def login():
    json_data = request.get_json()
    errors = UserLoginSchema().validate(json_data)
    if errors:
        return jsonify(errors), 400

    username = json_data['username']
    password = json_data['password']
    
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity={"id": user.id, "role": user.role})
        return jsonify(access_token=access_token), 200
    
    return jsonify({"message": "Invalid credentials"}), 401
