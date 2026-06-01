from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from database import get_db
from models import User, Login
from auth import hash_password, verify_password, create_token

auth_router = APIRouter(tags=["Authentication"])

def _register_user(email, name, password, role, db):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=email, name=name, password=hash_password(password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "Registration Successful", "user_id": f"UserID: {user.id}", "email": user.email}

def _login_user(data: Login, db):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User Not Found (Register First)")
    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid Password")
    token = create_token({"email": user.email, "role": user.role, "name": user.name})
    return {"message": "Login successful", "token": token, "role": user.role}

@auth_router.post("/register")
def register(
    email: str = Form(...), 
    name: str = Form(...),
    password: str = Form(...), 
    role: str = Form(...),
    db: Session = Depends(get_db)
):
    return _register_user(email, name, password, role, db)

@auth_router.post("/login")
def login(data: Login, db: Session = Depends(get_db)):
    return _login_user(data, db)

@auth_router.post("/auth/register")
def auth_register(
    email: str = Form(...), name: str = Form(...),
    password: str = Form(...), role: str = Form(...),
    db: Session = Depends(get_db)
):
    return _register_user(email, name, password, role, db)

@auth_router.post("/auth/login")
def auth_login(data: Login, db: Session = Depends(get_db)):
    return _login_user(data, db)
