from pydantic import BaseModel,EmailStr, Field
from pydantic import  root_validator

class User(BaseModel):
    username: str
    password: str
    role:str
    email: EmailStr
    confirm_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class Grade(BaseModel):
    pure_maths: float
    chemistry: float
    biology: float
    computer_science: float
    physics: float

    @root_validator(pre=True)
    def check_passwords_match(cls,values):
        password=values.get("password")
        confirm_password=values.get("confirm_password")
        if password != confirm_password:
            raise ValueError("Password do not match")
        return values