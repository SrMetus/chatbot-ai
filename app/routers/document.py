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
    """Split a text into overlapping word chunks.

    Uses CHUNK_SIZE words per chunk with CHUNK_OVERLAP words of
    sliding overlap between consecutive chunks.

    Args:
        text: The full text to split.

    Returns:
        list[str]: Ordered list of text chunks.
    """
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
    """Upload a PDF, extract text, chunk it, and store embeddings.

    Only PDF files up to 10 MB are accepted. Each chunk is embedded
    locally and persisted as a DocumentEmbedding row.

    Args:
        client_id: Target client ID.
        file: The PDF file to process.
        db: Database session.
        current_user: Authenticated admin user.

    Returns:
        dict: Confirmation message, chunk count, and a preview of the
            first 3 chunks.

    Raises:
        HTTPException 404: If the client does not exist.
        HTTPException 400: If the file is not a PDF, cannot be read,
            or has no extractable text.
        HTTPException 413: If the file exceeds 10 MB.
    """
    db_client = db.query(client_model.Client).filter(client_model.Client.id == client_id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    MAX_SIZE = 10 * 1024 * 1024
    if file.size and file.size > MAX_SIZE:
        raise HTTPException(status_code=413, detail="El archivo no puede superar los 10MB.")

    try:
        contents = file.file.read()
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read PDF file")

    if not full_text.strip():
        raise HTTPException(status_code=400, detail="PDF file is empty or has no extractable text")

    chunks = _split_into_chunks(full_text)
    filename = file.filename or ""

    stored = []
    for idx, chunk_text in enumerate(chunks):
        embedding = generate_embedding(chunk_text)
        doc = DocumentEmbedding(
            client_id=client_id,
            content=chunk_text,
            embedding=embedding,
            source_file=filename,
            chunk_index=idx,
        )
        db.add(doc)
        stored.append(chunk_text[:80])
    db.commit()

    return {
        "message": f"Document processed: {len(chunks)} chunks stored",
        "chunks_count": len(chunks),
        "preview": stored[:3],
    }
