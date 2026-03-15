import os
from pypdf import PdfReader
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings


def extract_text(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()
    text: str = ""
    
    if ext == ".pdf":
        reader = PdfReader(file_path)
        for page in reader.pages:
            content: str = page.extract_text()
            if content:
                text += content
    elif ext == ".docx":
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    else:
        raise ValueError("Unsupported file type,Instead upload (PDF or DOCX)")
    if text is None or text.strip() == "":
        raise ValueError("File is empty")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = splitter.split_text(text)

    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    embeddings = embedding_model.embed_documents(chunks)

    return chunks, embeddings



