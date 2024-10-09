from app import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    role = db.Column(db.String)  # 'student', 'teacher', or 'admin'
    
    grades = db.relationship('Grade', backref='student', lazy=True)

class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    pure_maths = db.Column(db.Float)
    chemistry = db.Column(db.Float)
    biology = db.Column(db.Float)
    computer_science = db.Column(db.Float)
    physics = db.Column(db.Float)
