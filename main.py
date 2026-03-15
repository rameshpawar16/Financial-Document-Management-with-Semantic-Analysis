from fastapi import FastAPI, APIRouter, Depends, Form, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import User, Login, Role
from auth import hash_password, verify_password, create_token
from dependencies import get_current_user
from rbac import rbac_router
from documents import documents_router
from rag.router import rag_router
from chat import chat_router
import os

app = FastAPI(title="Financial Document Management API")
router = APIRouter()

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Home pahe for registion
@app.get("/", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/admin/assign-role", response_class=HTMLResponse)
def assign_role_home(request: Request):
    return templates.TemplateResponse("role_assign.html", {"request": request})


def _register_user(email, name, password, role, db):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=email, name=name, password=hash_password(password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User Registered", "user_id": user.id, "email": user.email}

def _login_user(data: Login, db):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User Not Found (Register First)")
    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid Password")
    token = create_token({"email": user.email, "role": user.role, "name": user.name})
    return {"message": "Login successful", "token": token, "role": user.role}

# posts
@app.post("/register")
def register(
    email: str = Form(...), name: str = Form(...),
    password: str = Form(...), role: str = Form(...),
    db: Session = Depends(get_db)
):
    return _register_user(email, name, password, role, db)

@app.post("/login")
def login(data: Login, db: Session = Depends(get_db)):
    return _login_user(data, db)

@app.post("/auth/register")
def auth_register(
    email: str = Form(...), name: str = Form(...),
    password: str = Form(...), role: str = Form(...),
    db: Session = Depends(get_db)
):
    return _register_user(email, name, password, role, db)

@app.post("/auth/login")
def auth_login(data: Login, db: Session = Depends(get_db)):
    return _login_user(data, db)

#Utility routes
@router.get("/users/me")
def get_current_user_info(current_user=Depends(get_current_user)):
    return current_user

@router.get("/roles")
def get_roles(db: Session = Depends(get_db)):
    roles = db.query(Role).all()
    return [{"id": r.id, "name": r.name} for r in roles]

# ── Register all routers ──────────────────────────────────────────────────────
app.include_router(router)
app.include_router(rbac_router)
app.include_router(documents_router)
app.include_router(rag_router)
app.include_router(chat_router)
