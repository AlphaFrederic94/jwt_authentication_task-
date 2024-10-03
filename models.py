from pydantic import BaseModel

class User(BaseModel):
    username: str
    password: str
    role:str

class Token(BaseModel):
    access_token: str
    token_type: str

class Grade(BaseModel):
    pure_maths: float
    chemistry: float
    biology: float
    computer_science: float
    physics: float