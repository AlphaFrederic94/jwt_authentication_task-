import sqlite3

# Database connection
conn = sqlite3.connect('student_management.db', check_same_thread=False)
cursor = conn.cursor()

def create_tables():
    # Create users and grades tables if they don't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, 
        username TEXT UNIQUE, 
        email TEXT ,           
        password TEXT NOT NULL, 
        role TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS grades (
        student_id INTEGER, 
        pure_maths REAL, 
        chemistry REAL, 
        biology REAL, 
        computer_science REAL, 
        physics REAL, 
        FOREIGN KEY(student_id) REFERENCES users(id))''')
    
    conn.commit()