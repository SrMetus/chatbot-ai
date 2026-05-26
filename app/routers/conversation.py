import uuid
import time
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.classifier import process_chat
from app.schemas.conversation import MessageInput, MessageResponse
from app.models import client as client_model, conversation as conversation_model

router = APIRouter()

RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 20
_rate_store: dict[str, list[float]] = {}

def _check_rate(client_id: int, ip: str) -> None:
    """Enforce an in-memory rate limit per client+IP combination.

    Allows up to RATE_LIMIT_MAX requests inside a RATE_LIMIT_WINDOW
    (seconds) sliding window.

    Args:
        client_id: Client identifier used to scope the rate bucket.
        ip: Client IP address.

    Raises:
        HTTPException 429: When the rate limit is exceeded.
    """
    key = f"{client_id}:{ip}"
    now = time.time()
    timestamps = _rate_store.get(key, [])
    cutoff = now - RATE_LIMIT_WINDOW
    timestamps = [t for t in timestamps if t > cutoff]
    if len(timestamps) >= RATE_LIMIT_MAX:
        raise HTTPException(
            status_code=429,
            detail="Demasiadas solicitudes. Intenta en un momento.",
        )
    timestamps.append(now)
    _rate_store[key] = timestamps


@router.post("/{client_id}", response_model=MessageResponse)
def chat(client_id: int, message: MessageInput, request: Request, db: Session = Depends(get_db)):
    """Process a chat message and return the AI response.

    Applies rate limiting, looks up the client, delegates to the
    pipeline (FAQ cache → semantic match → classifier → RAG → model),
    and persists both user and assistant messages.

    Args:
        client_id: Target client ID.
        message: Message payload containing the user text and optional
            session_id.
        request: Incoming request (used to extract the client IP).

    Returns:
        MessageResponse: The AI reply and the session_id.

    Raises:
        HTTPException 404: If the client does not exist.
        HTTPException 429: If the rate limit is exceeded.
    """
    ip = request.client.host if request.client else "unknown"
    _check_rate(client_id, ip)

    db_client = db.query(client_model.Client).filter(client_model.Client.id == client_id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    session_id = message.session_id or str(uuid.uuid4())

    ai_response = process_chat(
        db=db,
        client=db_client,
        session_id=session_id,
        message=message.message,
    )

    user_message = conversation_model.Conversation(
        client_id=client_id,
        session_id=session_id,
        role="user",
        message=message.message,
    )
    db.add(user_message)

    ai_message = conversation_model.Conversation(
        client_id=client_id,
        session_id=session_id,
        role="assistant",
        message=ai_response,
    )
    db.add(ai_message)

    db.commit()

    return {"message": ai_response, "session_id": session_id}
