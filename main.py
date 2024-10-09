from flask import Flask
from app.database import init_db
from app.routes.auth_routes import routes as auth_routes
from app.routes.grade_routes import routes as grade_routes
from app.routes.admin_routes import routes as admin_routes
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Initialize the Flask app
app = Flask(__name__)

# Set the JWT secret key
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  # key is set in .env

# Initialize the JWTManager
jwt = JWTManager(app)

# Initialize the database
init_db(app)

# Register routes
app.register_blueprint(auth_routes, url_prefix='/auth')
app.register_blueprint(grade_routes, url_prefix='/grades')
app.register_blueprint(admin_routes, url_prefix='/admin')

# Example root route
@app.route('/')
def index():
    return {"message": "Welcome to the JWT authentication system!"}

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
