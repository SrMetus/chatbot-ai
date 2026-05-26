import io
import pdfplumber
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models import client as client_model
from app.models.embedding import DocumentEmbedding
from app.core.embeddings import generate_embedding

router = APIRouter()

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def _split_into_chunks(text: str) -> list[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        end = min(i + CHUNK_SIZE, len(words))
        chunk = " ".join(words[i:end])
        chunks.append(chunk)
        if end == len(words):
            break
        i += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


@router.post("/{client_id}/upload")
def upload_document(
    client_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_client = db.query(client_model.Client).filter(client_model.Client.id == client_id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    try:
        contents = file.file.read()
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read PDF file")

    if not full_text.strip():
        raise HTTPException(status_code=400, detail="PDF file is empty or has no extractable text")

    chunks = _split_into_chunks(full_text)

    stored = []
    for chunk_text in chunks:
        embedding = generate_embedding(chunk_text)
        doc = DocumentEmbedding(
            client_id=client_id,
            content=chunk_text,
            embedding=embedding,
        )
        db.add(doc)
        stored.append(chunk_text[:80])
    db.commit()

    return {
        "message": f"Document processed: {len(chunks)} chunks stored",
        "chunks_count": len(chunks),
        "preview": stored[:3],
    }
