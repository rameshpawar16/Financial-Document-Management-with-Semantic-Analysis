from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Role
from dependencies import get_current_user

user_router = APIRouter(tags=["Users"])

@user_router.get("/users/me")
def get_current_user_info(current_user=Depends(get_current_user)):
    return current_user

@user_router.get("/roles")
def get_roles(db: Session = Depends(get_db)):
    roles = db.query(Role).all()
    return [{"id": r.id, "name": r.name} for r in roles]

@user_router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
