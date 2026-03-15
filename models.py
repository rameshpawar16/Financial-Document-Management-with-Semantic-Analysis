from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from database import Base
from pydantic import BaseModel
from typing import List, Optional


class Login(BaseModel):
    email: str
    password: str

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(String)


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    company_name = Column(String)
    document_type = Column(String)
    file_path = Column(String)
    uploaded_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String, nullable=True)


class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role_id = Column(Integer, ForeignKey("roles.id"))


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"))
    permission_id = Column(Integer, ForeignKey("permissions.id"))


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True)
    session_id = Column(String, index=True)
    user_email = Column(String)
    question = Column(String)
    response = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class AssignRolesRequest(BaseModel):
    user_id: int
    role_id: int

class CreateRoleRequest(BaseModel):
    name: str

class QuestionRequest(BaseModel):
    question: str
