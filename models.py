from pydantic import BaseModel, EmailStr, Field, validator
from datetime import date, datetime

class User(BaseModel):
    firstName: str
    lastName: str
    password: str
    role: str
    dateOfBirth: date
    email: EmailStr

    @validator('dateOfBirth', pre=True)
    def parse_date_of_birth(cls, value):
        if isinstance(value, str):  # Check if the input is a string
            try:
                # Try parsing MM/DD/YYYY format
                return datetime.strptime(value, '%m/%d/%Y').date()
            except ValueError:
                raise ValueError("Date of Birth must be in MM/DD/YYYY format")
        return value

class UserResponse(BaseModel):
    id: int
    email: str
    firstName: str
    lastName: str
    dateOfBirth: str
    role: str
    
class UserUpdate(BaseModel):
    email: str
    firstName: str
    lastName: str
    dateOfBirth: str
    
class Token(BaseModel):
    access_token: str
    token_type: str

class Grade(BaseModel):
    pure_maths: float
    chemistry: float
    biology: float
    computer_science: float
    physics: float