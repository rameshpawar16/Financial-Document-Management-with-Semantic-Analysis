from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

ui_router = APIRouter(tags=["UI Pages"])
templates = Jinja2Templates(directory="templates")

@ui_router.get("/", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@ui_router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@ui_router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@ui_router.get("/admin/assign-role", response_class=HTMLResponse)
def assign_role_home(request: Request):
    return templates.TemplateResponse("role_assign.html", {"request": request})
