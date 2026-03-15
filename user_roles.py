from models import UserRole, Role
from fastapi import Depends,HTTPException
from sqlalchemy.orm import Session
from dependencies import get_current_user
from database import get_db

def get_user_role(user_id, db):

    role = db.query(Role)\
        .join(UserRole, Role.id == UserRole.role_id)\
        .filter(UserRole.user_id == user_id)\
        .first()
    if not role:
        raise HTTPException(status_code=404,detail="Role not found for this user")
    return role.name

def require_role(required_role: str):
    def role_checker(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
        role = get_user_role(current_user.get("id"), db)

        if role != required_role:
            raise HTTPException(status_code=403,detail="Access denied")
        return current_user
    return role_checker