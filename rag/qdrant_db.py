from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue
from langchain_huggingface import HuggingFaceEmbeddings
import uuid

client = QdrantClient(path="qdrant_data")
collection_name = "financial_docs"

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def create_collection():
    """Create collection only if it doesn't exist."""
    existing = [c.name for c in client.get_collections().collections]
    if collection_name not in existing:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )


def store_in_qdrant(chunks, embeddings, document_id: int = None):
    """Store chunks with document_id in payload for later filtering/deletion."""
    points = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        point_id = abs(hash(f"{document_id}_{i}")) % (2**63)
        points.append(
            PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "text": chunk,
                    "document_id": document_id
                }
            )
        )
    client.upsert(collection_name=collection_name, points=points)
    return len(points)


def delete_document_vectors(document_id: int):
    """Remove all vector points belonging to a specific document."""
    client.delete(
        collection_name=collection_name,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id)
                )
            ]
        )
    )


def get_document_chunks(document_id: int):
    """Retrieve all stored chunks for a specific document."""
    results, _ = client.scroll(
        collection_name=collection_name,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id)
                )
            ]
        ),
        limit=100,
        with_payload=True
    )
    return [r.payload["text"] for r in results]


def search_query(query: str, document_id: int = None, top_k: int = 20):
    """Semantic search, optionally filtered to a specific document."""
    query_vector = embedding_model.embed_query(query)

    search_filter = None
    if document_id is not None:
        search_filter = Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id)
                )
            ]
        )

    results = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k,
        query_filter=search_filter
    )

    return [res.payload["text"] for res in results]
