from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models import Document
from dependencies import get_current_user, role_required
from rag.load_chunk import extract_text
from rag.qdrant_db import create_collection, store_in_qdrant,search_query, delete_document_vectors, get_document_chunks
from rag.reranking import rerank

rag_router = APIRouter(prefix="/rag", tags=["RAG"])

class SearchRequest(BaseModel):
    query: str
    document_id: int = None   

@rag_router.post("/index-document")
def index_document(
    document_id: int,
    db: Session = Depends(get_db),
    user=Depends(role_required(["admin", "financial analyst"]))
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    try:
        chunks, embeddings = extract_text(doc.file_path)
        create_collection()
        count = store_in_qdrant(chunks, embeddings, document_id=document_id)
        return {
            "message": "Document indexed successfully",
            "document_id": document_id,
            "chunks_stored": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")

@rag_router.delete("/remove-document/{document_id}")
def remove_document_vectors(
    document_id: int,
    db: Session = Depends(get_db),
    user=Depends(role_required(["admin"]))
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    delete_document_vectors(document_id)
    return {
        "message": f"Embeddings for document '{doc.title}' removed from vector DB",
        "document_id": document_id
    }

@rag_router.post("/search")
def semantic_search(
    request: SearchRequest,
    user=Depends(get_current_user)
):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    results = search_query(request.query, document_id=request.document_id, top_k=20)

    if not results:
        return {"query": request.query, "results": []}
    
    # first 5
    ranked = rerank(request.query, results, 5)

    return {
        "query": request.query,
        "total_retrieved": len(results),
        "results": ranked
    }

@rag_router.get("/context/{document_id}")
def get_document_context(
    document_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    chunks = get_document_chunks(document_id)
    return {
        "document_id": document_id,
        "title": doc.title,
        "total_chunks": len(chunks),
        "chunks": chunks
    }
