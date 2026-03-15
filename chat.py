from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from database import get_db
from models import ChatHistory
from dependencies import get_current_user
from typing import Optional
import json

chat_router = APIRouter(prefix="/chat", tags=["Chat History"])


class SaveChatRequest(BaseModel):
    session_id: str
    question: str
    response: str


# POST /chat/save
@chat_router.post("/save")
def save_chat(
    request: SaveChatRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    chat = ChatHistory(
        session_id=request.session_id,
        user_email=user["email"],
        question=request.question,
        response=request.response
    )
    db.add(chat)
    db.commit()
    return {"message": "Chat saved"}


# GET /chat/sessions
@chat_router.get("/sessions")
def get_chat_sessions(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Get all unique chat sessions for the current user, with first question as title."""
    sessions = (
        db.query(
            ChatHistory.session_id,
            func.min(ChatHistory.question).label("first_question"),
            func.min(ChatHistory.created_at).label("started_at"),
            func.count(ChatHistory.id).label("message_count")
        )
        .filter(ChatHistory.user_email == user["email"])
        .group_by(ChatHistory.session_id)
        .order_by(func.max(ChatHistory.created_at).desc())
        .all()
    )
    return [
        {
            "session_id": s.session_id,
            "title": s.first_question[:40] + "..." if len(s.first_question) > 40 else s.first_question,
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "message_count": s.message_count
        }
        for s in sessions
    ]


# GET /chat/history/{session_id} 
@chat_router.get("/history/{session_id}")
def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Get all messages in a specific chat session."""
    chats = (
        db.query(ChatHistory)
        .filter(ChatHistory.session_id == session_id, ChatHistory.user_email == user["email"])
        .order_by(ChatHistory.created_at.asc())
        .all()
    )
    return [
        {
            "question": c.question,
            "response": c.response,
            "created_at": c.created_at.isoformat() if c.created_at else None
        }
        for c in chats
    ]
