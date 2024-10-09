from flask import Flask
from app.database import init_db  # Import your database initialization function

# Initialize the Flask app
app = Flask(__name__)

# Initialize the database
init_db(app)

# Optionally, you can expose the db instance for import in other modules
from app.database import db
