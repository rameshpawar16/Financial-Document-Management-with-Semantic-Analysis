from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from rbac import rbac_router
from documents import documents_router
from chat import chat_router
from rag.router import rag_router

# Modular routers
from routers.ui import ui_router
from routers.auth import auth_router
from routers.users import user_router

app = FastAPI(title="Financial Document Management API")

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register all routers ──────────────────────────────────────────────────────
app.include_router(ui_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(rbac_router)
app.include_router(documents_router)
app.include_router(rag_router)
app.include_router(chat_router)
