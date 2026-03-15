from transformers import AutoModelForSequenceClassification,AutoTokenizer
import torch

tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-reranker-base")
model = AutoModelForSequenceClassification.from_pretrained("BAAI/bge-reranker-base")

def rerank(query, documents, top_k=5):

    if not documents:
        return []
    
    pairs = [[query, doc] for doc in documents]

    inputs = tokenizer(
        pairs,
        padding=True,
        truncation=True,
        return_tensors="pt"
    )

    with torch.no_grad():
        logits = model(**inputs).logits

    scores = logits.squeeze()

    if scores.dim() == 0:
        scores = [scores.item()]
    else:
        scores = scores.tolist()

    scored_docs = [{"document": doc, "score": score} for doc, score in zip(documents, scores)]

    scored_docs = sorted(scored_docs,key=lambda x: x["score"],reverse=True)

    top_docs = scored_docs[:top_k]

    # print("Top reranked docs:", top_docs)

    return top_docs