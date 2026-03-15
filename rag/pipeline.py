from rag.load_chunk import extract_text
from rag.qdrant_db import create_collection, store_in_qdrant


def process_document(file_path: str, document_id: int = None):
    """Extract text, chunk, embed, and store in Qdrant."""
    chunks, embeddings = extract_text(file_path)
    create_collection()
    count = store_in_qdrant(chunks, embeddings, document_id=document_id)
    print(f"Stored {count} chunks for document_id={document_id}")
    return count