from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from database import get_db
from models import Document, User
from dependencies import get_current_user, role_required
from rag.pipeline import process_document
import os
import shutil
from datetime import datetime

documents_router = APIRouter(prefix="/documents", tags=["Documents"])


# ── POST /documents/upload ────────────────────────────────────────────────────
@documents_router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    company_name: str = Form(...),
    document_type: str = Form(...),
    db: Session = Depends(get_db),
    user=Depends(role_required(["admin", "financial analyst"]))
):
    os.makedirs("documents", exist_ok=True)
    file_path = f"documents/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    doc = Document(
        title=title,
        company_name=company_name,
        document_type=document_type,
        file_path=file_path,
        uploaded_by=user["email"],
        created_at=datetime.utcnow()
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Trigger RAG indexing
    try:
        process_document(file_path)
    except Exception as e:
        print(f"RAG indexing warning: {e}")

    return {
        "message": "Document uploaded successfully",
        "document_id": doc.id,
        "title": doc.title,
        "company_name": doc.company_name,
        "document_type": doc.document_type,
        "uploaded_by": doc.uploaded_by,
        "created_at": doc.created_at.isoformat()
    }


# GET /documents
@documents_router.get("/")
def get_all_documents(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    docs = db.query(Document).all()
    return [
        {
            "document_id": d.id,
            "title": d.title,
            "company_name": d.company_name,
            "document_type": d.document_type,
            "uploaded_by": d.uploaded_by,
            "created_at": d.created_at.isoformat() if d.created_at else None
        }
        for d in docs
    ]


@documents_router.get("/search")
def search_documents(
    title: str = None,
    document_type: str = None,
    company_name: str = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    query = db.query(Document)
    if title:
        query = query.filter(Document.title.ilike(f"%{title}%"))
    if document_type:
        query = query.filter(Document.document_type.ilike(f"%{document_type}%"))
    if company_name:
        query = query.filter(Document.company_name.ilike(f"%{company_name}%"))

    docs = query.all()
    if not docs:
        return {"message": "No documents found", "results": []}

    return {
        "results": [
            {
                "document_id": d.id,
                "title": d.title,
                "company_name": d.company_name,
                "document_type": d.document_type,
                "uploaded_by": d.uploaded_by,
                "created_at": d.created_at.isoformat() if d.created_at else None
            }
            for d in docs
        ]
    }


@documents_router.get("/{document_id}")
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "document_id": doc.id,
        "title": doc.title,
        "company_name": doc.company_name,
        "document_type": doc.document_type,
        "file_path": doc.file_path,
        "uploaded_by": doc.uploaded_by,
        "created_at": doc.created_at.isoformat() if doc.created_at else None
    }


# DELETE /documents
@documents_router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    user=Depends(role_required(["admin"]))
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Remove the physical file
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    db.delete(doc)
    db.commit()

    return {"message": f"Document '{doc.title}' deleted successfully"}
