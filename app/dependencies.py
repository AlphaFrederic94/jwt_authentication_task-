from fastapi import Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from app.models import User
from app import SessionLocal

def get_current_user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    current_user = Authorize.get_jwt_subject()
    db = SessionLocal()
    user = db.query(User).filter(User.id == current_user['id']).first()
    db.close()
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user

def role_required(required_role: str):
    def role_checker(user: User = Depends(get_current_user)):
        if user.role != required_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
        return user
    return role_checker
